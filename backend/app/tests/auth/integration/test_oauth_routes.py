from unittest.mock import MagicMock, patch

import pytest
from httpx2 import AsyncClient
from itsdangerous import URLSafeTimedSerializer
from pydantic import SecretStr
from sqlalchemy import select

from app.core.config import Settings
from app.users.models import User


def _make_state_cookie(settings: Settings, provider: str, state: str) -> str:
    serializer = URLSafeTimedSerializer(
        settings.secret_key.get_secret_value(), salt="oauth-state"
    )
    return serializer.dumps({"state": state, "provider": provider})


@pytest.mark.asyncio
async def test_oauth_login_redirects_to_google(
    db_client: AsyncClient, test_settings: Settings
):
    test_settings.google_client_id = "test-google-id"
    test_settings.google_client_secret = SecretStr("test-google-secret")

    response = await db_client.get(
        "/api/v1/auth/oauth/google/login", follow_redirects=False
    )

    assert response.status_code == 302
    location = response.headers.get("Location", "")
    assert location.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "client_id=test-google-id" in location
    assert "response_type=code" in location
    assert "scope=openid+email+profile" in location
    assert response.cookies.get("oauth_state") is not None


@pytest.mark.asyncio
async def test_oauth_login_unavailable_when_missing_credentials(
    db_client: AsyncClient, test_settings: Settings
):
    test_settings.google_client_id = None
    test_settings.google_client_secret = None

    response = await db_client.get(
        "/api/v1/auth/oauth/google/login", follow_redirects=False
    )

    assert response.status_code == 303
    location = response.headers.get("Location", "")
    assert "error=provider_unavailable" in location


@pytest.mark.asyncio
async def test_oauth_login_invalid_provider(
    db_client: AsyncClient, test_settings: Settings
):
    response = await db_client.get(
        "/api/v1/auth/oauth/facebook/login", follow_redirects=False
    )

    assert response.status_code == 303
    location = response.headers.get("Location", "")
    assert "error=invalid_provider" in location


@pytest.mark.asyncio
async def test_oauth_callback_invalid_state(
    db_client: AsyncClient, test_settings: Settings
):
    test_settings.google_client_id = "test-google-id"
    test_settings.google_client_secret = SecretStr("test-google-secret")

    db_client.cookies.set("oauth_state", "bad-signature")
    response = await db_client.get(
        "/api/v1/auth/oauth/google/callback",
        params={"code": "123", "state": "invalid-state"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "error=oauth_state" in response.headers.get("Location", "")


@pytest.mark.asyncio
async def test_oauth_callback_denied(db_client: AsyncClient, test_settings: Settings):
    test_settings.google_client_id = "test-google-id"
    test_settings.google_client_secret = SecretStr("test-google-secret")

    state = "secure-random-state"
    cookie_val = _make_state_cookie(test_settings, "google", state)

    db_client.cookies.set("oauth_state", cookie_val)
    response = await db_client.get(
        "/api/v1/auth/oauth/google/callback",
        params={"error": "access_denied", "state": state},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "error=oauth_denied" in response.headers.get("Location", "")


@pytest.mark.asyncio
async def test_oauth_callback_google_creates_and_reauthenticates_user(
    db_client: AsyncClient, db_session, test_settings: Settings
):
    test_settings.google_client_id = "test-google-id"
    test_settings.google_client_secret = SecretStr("test-google-secret")

    state = "random-oauth-state-1234"
    cookie_val = _make_state_cookie(test_settings, "google", state)

    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"id_token": "fake-google-jwt"}
    mock_token_resp.raise_for_status.return_value = None

    mock_claims_resp = MagicMock()
    mock_claims_resp.json.return_value = {
        "aud": "test-google-id",
        "iss": "https://accounts.google.com",
        "email": "oauth.user@example.com",
        "email_verified": True,
        "name": "OAuth User",
        "sub": "google-user-id",
    }
    mock_claims_resp.raise_for_status.return_value = None

    db_client.cookies.set("oauth_state", cookie_val)
    with (
        patch("httpx.AsyncClient.post", return_value=mock_token_resp),
        patch("httpx.AsyncClient.get", return_value=mock_claims_resp),
    ):
        response = await db_client.get(
            "/api/v1/auth/oauth/google/callback",
            params={"code": "valid-auth-code", "state": state},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers.get("Location", "").endswith("/semana/perfil")
    assert response.cookies.get("refresh_token") is not None

    user = await db_session.scalar(
        select(User).where(User.email == "oauth.user@example.com")
    )
    assert user is not None
    assert user.name == "OAuth User"
    assert user.oauth_provider == "google"
    assert user.oauth_subject == "google-user-id"
    assert user.is_verified is True
    assert user.password_hash is None

    repeat_state = "returning-google-state"
    db_client.cookies.set(
        "oauth_state", _make_state_cookie(test_settings, "google", repeat_state)
    )
    with (
        patch("httpx.AsyncClient.post", return_value=mock_token_resp),
        patch("httpx.AsyncClient.get", return_value=mock_claims_resp),
    ):
        response = await db_client.get(
            "/api/v1/auth/oauth/google/callback",
            params={"code": "returning-auth-code", "state": repeat_state},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers.get("Location", "").endswith("/semana/perfil")
    returning_user = await db_session.scalar(
        select(User).where(User.oauth_subject == "google-user-id")
    )
    assert returning_user is not None
    assert returning_user.id == user.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("oauth_provider", "oauth_subject", "deleted"),
    [
        (None, None, False),
        ("github", "github-user-id", False),
        ("google", "google-user-id", True),
    ],
)
async def test_oauth_callback_blocks_existing_email(
    db_client: AsyncClient,
    db_session,
    deleted_user_factory,
    user_factory,
    test_settings: Settings,
    oauth_provider: str | None,
    oauth_subject: str | None,
    deleted: bool,
):
    if deleted:
        user = await deleted_user_factory(email="existing-pwd@example.com")
    else:
        user = await user_factory(email="existing-pwd@example.com")
    user.oauth_provider = oauth_provider
    user.oauth_subject = oauth_subject
    await db_session.flush()

    test_settings.google_client_id = "test-google-id"
    test_settings.google_client_secret = SecretStr("test-google-secret")

    state = "state-conflict"
    cookie_val = _make_state_cookie(test_settings, "google", state)

    mock_token_resp = MagicMock()
    mock_token_resp.json.return_value = {"id_token": "fake-jwt"}
    mock_token_resp.raise_for_status.return_value = None

    mock_claims_resp = MagicMock()
    mock_claims_resp.json.return_value = {
        "aud": "test-google-id",
        "iss": "https://accounts.google.com",
        "email": "existing-pwd@example.com",
        "email_verified": True,
        "name": "Imposter",
        "sub": "google-user-id",
    }
    mock_claims_resp.raise_for_status.return_value = None

    db_client.cookies.set("oauth_state", cookie_val)
    with (
        patch("httpx.AsyncClient.post", return_value=mock_token_resp),
        patch("httpx.AsyncClient.get", return_value=mock_claims_resp),
    ):
        response = await db_client.get(
            "/api/v1/auth/oauth/google/callback",
            params={"code": "code", "state": state},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert "error=email_exists" in response.headers.get("Location", "")
    assert user.oauth_provider == oauth_provider
    assert user.oauth_subject == oauth_subject
    assert user.password_hash is not None
    assert (user.deleted_at is not None) is deleted
