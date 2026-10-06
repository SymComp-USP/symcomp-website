import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import email as email_service
from app.auth import services
from app.auth.dependencies import get_current_user
from app.auth.models import AuthTokenPurpose
from app.auth.schemas import (
    AuthTokenRequest,
    EmailRequest,
    PasswordResetRequest,
    RequestedScopesBody,
    Token,
)
from app.auth.scopes import DEFAULT_SCOPES, KNOWN_SCOPES, Scope
from app.core.config import AppEnv
from app.core.database import get_session
from app.core.exceptions.app_errors import (
    BadRequestError,
    ForbiddenError,
    UnauthorizedError,
)
from app.users import services as user_services
from app.users.models import User
from app.users.schemas import UserMe, UserUpdate

router = APIRouter(tags=["auth"])
GENERIC_EMAIL_RESPONSE = {"detail": "If the account exists, an email was sent."}
VERIFICATION_RESEND_COOLDOWN = timedelta(minutes=15)
logger = logging.getLogger(__name__)


@router.post("/login")
async def login_with_password(
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await services.authenticate(
        db_session, form_data.username, form_data.password
    )

    if user is None:
        raise UnauthorizedError(detail="Invalid username or password")

    requested_scopes = form_data.scopes if form_data.scopes else DEFAULT_SCOPES
    requested_set = set(requested_scopes)

    unknown = requested_set - KNOWN_SCOPES
    if unknown:
        raise UnauthorizedError(detail=f"Unknown scopes: {sorted(unknown)}")

    grantable = services.get_grantable_scopes(user)
    not_allowed = requested_set - grantable
    if not_allowed:
        raise ForbiddenError(detail=f"Scopes not allowed: {sorted(not_allowed)}")

    if user.is_admin and Scope.ADMIN not in requested_set:
        requested_scopes = list(requested_scopes) + [Scope.ADMIN]

    # Access Token: contém a identificação do usuário ("data.sub")
    # e os escopos de acesso ("data.scopes")
    access_token = services.create_access_token(user.id, requested_scopes)

    # ID Token: contém dados da identidade do usuário
    id_token = await services.create_id_token(db_session, requested_scopes, user.id)

    refresh_token_str = await services.create_refresh_token(
        db_session, user.id, requested_scopes
    )

    response.set_cookie(**services.build_refresh_token_cookie(refresh_token_str))

    return Token(access_token=access_token, id_token=id_token, token_type="bearer")


@router.post("/verify-email")
async def verify_email(
    payload: AuthTokenRequest,
    db_session: Annotated[AsyncSession, Depends(get_session)],
):
    token = await services.consume_auth_token(
        db_session, payload.token, AuthTokenPurpose.VERIFY_EMAIL
    )
    if token is None:
        raise BadRequestError("Invalid or expired verification token")

    user = await user_services.get_user_by_id(db_session, token.user_id)
    if user is None:
        raise BadRequestError("Invalid or expired verification token")
    user.is_verified = True
    await db_session.flush()
    return {"detail": "Email verified."}


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
async def resend_verification_email(
    payload: EmailRequest,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    mailer: Annotated[
        email_service.EmailService, Depends(email_service.get_email_service)
    ],
):
    user = await user_services.get_user_by_email(db_session, str(payload.email))
    if user is not None and not user.is_verified:
        if await services.has_recent_auth_token(
            db_session,
            user.id,
            AuthTokenPurpose.VERIFY_EMAIL,
            datetime.now(UTC) - VERIFICATION_RESEND_COOLDOWN,
        ):
            return GENERIC_EMAIL_RESPONSE
        token = await services.create_auth_token(
            db_session, user.id, AuthTokenPurpose.VERIFY_EMAIL, timedelta(hours=24)
        )
        try:
            await mailer.send_verification_email(user.email, user.name, token)
        except Exception:
            logger.exception("Verification email delivery failed")
    return GENERIC_EMAIL_RESPONSE


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    payload: EmailRequest,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    mailer: Annotated[
        email_service.EmailService, Depends(email_service.get_email_service)
    ],
):
    user = await user_services.get_user_by_email(db_session, str(payload.email))
    if user is not None and user.password_hash is not None:
        token = await services.create_auth_token(
            db_session, user.id, AuthTokenPurpose.RESET_PASSWORD, timedelta(hours=1)
        )
        try:
            await mailer.send_password_reset_email(user.email, user.name, token)
        except Exception:
            logger.exception("Password reset email delivery failed")
    return GENERIC_EMAIL_RESPONSE


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    payload: PasswordResetRequest,
    db_session: Annotated[AsyncSession, Depends(get_session)],
):
    token = await services.consume_auth_token(
        db_session, payload.token, AuthTokenPurpose.RESET_PASSWORD
    )
    if token is None:
        raise BadRequestError("Invalid or expired password reset token")

    user = await user_services.get_user_by_id(db_session, token.user_id)
    if user is None or user.password_hash is None:
        raise BadRequestError("Invalid or expired password reset token")

    await user_services.update_user(
        db_session, user, UserUpdate(password=payload.password)
    )
    await services.revoke_user_refresh_tokens(db_session, user.id)
    return {"detail": "Password reset."}


@router.get("/me", response_model=UserMe)
async def get_my_info(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    user = await user_services.get_user_profile_by_id(db_session, current_user.id)
    if user is None:
        raise UnauthorizedError(detail="Inexistent or inactive user")
    return user


@router.post("/refresh")
async def refresh_token(
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    requested_scopes_body: RequestedScopesBody | None = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    """Cria um novo access token e rotaciona o refresh token (revoga o atual e cria um novo)"""

    if not refresh_token:
        raise UnauthorizedError(detail="Invalid refresh token")

    scopes = (
        requested_scopes_body.requested_scopes
        if requested_scopes_body is not None
        else None
    )

    result = await services.refresh_access_token(db_session, refresh_token, scopes)

    response.set_cookie(**services.build_refresh_token_cookie(result.refresh_token))

    return Token(access_token=result.access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_session)],
):
    token_str = request.cookies.get("refresh_token")

    if token_str is not None:
        await services.revoke_refresh_token(db_session, token_str)

    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=services.get_settings().app_env == AppEnv.production,
        samesite="lax",
    )
