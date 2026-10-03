from __future__ import annotations

import logging
import secrets
from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services as auth_services
from app.auth.scopes import DEFAULT_SCOPES, Scope
from app.core.config import AppEnv, get_settings
from app.core.database import get_session
from app.users.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/oauth", tags=["auth"])
STATE_COOKIE = "oauth_state"


def _serializer():
    return URLSafeTimedSerializer(
        get_settings().secret_key.get_secret_value(), salt="oauth-state"
    )


def _credentials(provider: str):
    s = get_settings()
    if provider == "google":
        return (
            s.google_client_id,
            s.google_client_secret.get_secret_value()
            if s.google_client_secret
            else None,
        )
    if provider == "github":
        return (
            s.github_client_id,
            s.github_client_secret.get_secret_value()
            if s.github_client_secret
            else None,
        )
    return None, None


@router.get("/{provider}/login")
async def oauth_login(provider: str):
    frontend = str(get_settings().frontend_base_url).rstrip("/")
    if provider not in ("google", "github"):
        return RedirectResponse(
            f"{frontend}/semana/login?error=invalid_provider", status_code=303
        )

    client_id, _ = _credentials(provider)
    if not client_id:
        return RedirectResponse(
            f"{frontend}/semana/login?error=provider_unavailable", status_code=303
        )

    state = secrets.token_urlsafe(32)
    signed = _serializer().dumps({"state": state, "provider": provider})
    callback = f"{str(get_settings().oauth_redirect_base).rstrip('/')}/api/v1/auth/oauth/{provider}/callback"
    if provider == "google":
        params = {
            "client_id": client_id,
            "redirect_uri": callback,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account",
        }
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    else:
        params = {
            "client_id": client_id,
            "redirect_uri": callback,
            "scope": "read:user user:email",
            "state": state,
        }
        url = "https://github.com/login/oauth/authorize?" + urlencode(params)

    redirect = RedirectResponse(url, status_code=302)
    redirect.set_cookie(
        STATE_COOKIE,
        signed,
        httponly=True,
        secure=get_settings().app_env == AppEnv.production,
        samesite="lax",
        max_age=600,
    )
    return redirect


@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    frontend = str(get_settings().frontend_base_url).rstrip("/")

    def fail(code: str):
        r = RedirectResponse(f"{frontend}/semana/login?error={code}", status_code=303)
        r.delete_cookie(STATE_COOKIE)
        return r

    if provider not in ("google", "github"):
        return fail("invalid_provider")

    client_id, client_secret = _credentials(provider)
    if not client_id or not client_secret:
        return fail("provider_unavailable")

    try:
        signed = _serializer().loads(request.cookies.get(STATE_COOKIE, ""), max_age=600)
    except BadSignature:
        logger.warning("OAuth state cookie has bad or expired signature")
        return fail("oauth_state")

    if signed.get("provider") != provider or not secrets.compare_digest(
        signed.get("state", ""), request.query_params.get("state", "")
    ):
        logger.warning("OAuth state verification failed for provider: %s", provider)
        return fail("oauth_state")

    code = request.query_params.get("code")
    if not code or request.query_params.get("error"):
        logger.info(
            "OAuth authorization denied or cancelled for provider: %s", provider
        )
        return fail("oauth_denied")

    callback = f"{str(get_settings().oauth_redirect_base).rstrip('/')}/api/v1/auth/oauth/{provider}/callback"
    try:
        async with httpx.AsyncClient(
            timeout=12, headers={"Accept": "application/json"}
        ) as client:
            if provider == "google":
                token_res = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": callback,
                        "grant_type": "authorization_code",
                    },
                )
                token_res.raise_for_status()
                id_token = token_res.json()["id_token"]
                claims_res = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": id_token},
                )
                claims_res.raise_for_status()
                profile = claims_res.json()
                if profile.get("aud") != client_id or profile.get("iss") not in (
                    "accounts.google.com",
                    "https://accounts.google.com",
                ):
                    logger.warning("Google ID token validation mismatch (aud/iss)")
                    return fail("oauth_invalid_profile")
                email = profile.get("email", "")
                verified = profile.get("email_verified") in (True, "true")
                name = profile.get("name") or email.split("@", 1)[0]
            else:
                token_res = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": callback,
                    },
                )
                token_res.raise_for_status()
                access = token_res.json().get("access_token")
                if not access:
                    return fail("oauth_profile")
                headers = {
                    "Authorization": f"Bearer {access}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                }
                user_res = await client.get(
                    "https://api.github.com/user", headers=headers
                )
                emails_res = await client.get(
                    "https://api.github.com/user/emails", headers=headers
                )
                user_res.raise_for_status()
                emails_res.raise_for_status()
                profile = user_res.json()
                chosen = next(
                    (
                        e
                        for e in emails_res.json()
                        if e.get("primary") and e.get("verified")
                    ),
                    None,
                )
                email = chosen.get("email", "") if chosen else ""
                verified = bool(chosen)
                name = (
                    profile.get("name")
                    or profile.get("login")
                    or email.split("@", 1)[0]
                )
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        logger.warning("OAuth exchange error with provider %s: %s", provider, exc)
        return fail("oauth_provider_error")

    email = email.strip().lower()
    name = " ".join(str(name).split())[:255]
    if not email or not verified or not name:
        return fail("oauth_unverified_email" if not verified else "oauth_profile")

    user = await db.scalar(
        select(User).where(func.lower(User.email) == email).with_for_update()
    )
    if user is not None and user.deleted_at is None and user.oauth_provider is None:
        return fail("email_exists")
    if user is not None and user.deleted_at is not None:
        user.deleted_at = None
        user.name = name
        user.password_hash = None
        user.oauth_provider = provider
        user.is_admin = False
        user.is_verified = True
    elif user is None:
        user = User(
            email=email,
            name=name,
            password_hash=None,
            oauth_provider=provider,
            is_verified=True,
            is_admin=False,
        )
        db.add(user)
        await db.flush()
    else:
        # OAuth-origin accounts may authenticate with either configured provider.
        user.is_verified = True

    scopes = list(DEFAULT_SCOPES)
    if user.is_admin:
        scopes.append(Scope.ADMIN)

    refresh = await auth_services.create_refresh_token(db, user.id, scopes)
    redirect = RedirectResponse(f"{frontend}/semana/perfil", status_code=303)
    redirect.set_cookie(**auth_services.build_refresh_token_cookie(refresh))
    redirect.delete_cookie(STATE_COOKIE)
    return redirect
