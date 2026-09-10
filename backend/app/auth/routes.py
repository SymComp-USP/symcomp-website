from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services
from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    InvalidPasswordException,
    InvalidRefreshTokenException,
    Token,
)
from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.users.models import User

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login_with_password(
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
):
    user = await services.authenticate(
        db_session, form_data.username, form_data.password
    )

    if user is None:
        raise InvalidPasswordException()

    access_token = services.create_access_token(data={"sub": user.email})
    refresh_token_str = await services.create_refresh_token(db_session, user.id)

    refresh_expire_time_seconds = settings.refresh_token_expire_days * 24 * 60 * 60

    response.set_cookie(
        key="refresh_token",
        value=refresh_token_str,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=refresh_expire_time_seconds,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
async def get_my_info(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.post("/refresh")
async def refresh_token(
    request: Request, db_session: Annotated[AsyncSession, Depends(get_session)]
):
    token_str = request.cookies.get("refresh_token")

    if not token_str:
        raise InvalidRefreshTokenException()

    new_access_token = await services.refresh_access_token(db_session, token_str)

    return Token(access_token=new_access_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    db_session: Annotated[AsyncSession, Depends(get_session)],
):
    token_str = request.cookies.get("refresh_token")

    if token_str is None:
        response.delete_cookie("refresh_token")
        return

    await services.revoke_refresh_token(db_session, token_str)

    response.delete_cookie(
        key="refresh_token", httponly=True, secure=True, samesite="lax"
    )
