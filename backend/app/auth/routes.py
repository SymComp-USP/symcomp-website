from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import services
from app.auth.dependencies import get_current_user
from app.auth.schemas import RequestedScopesBody, Token
from app.auth.scopes import DEFAULT_SCOPES, KNOWN_SCOPES, Scope
from app.core.database import get_session
from app.core.exceptions.app_errors import UnauthorizedError
from app.users.models import User

router = APIRouter(tags=["auth"])


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

    unknown = set(requested_scopes) - KNOWN_SCOPES
    if unknown:
        raise UnauthorizedError(detail=f"Unknown scopes: {sorted(unknown)}")

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


@router.get("/me")
async def get_my_info(
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    return current_user


@router.post("/refresh")
async def refresh_token(
    request: Request,
    db_session: Annotated[AsyncSession, Depends(get_session)],
    requested_scopes_body: RequestedScopesBody | None = None,
):
    token_str = request.cookies.get("refresh_token")

    if not token_str:
        raise UnauthorizedError(detail="Invalid refresh token")

    scopes = (
        requested_scopes_body.requested_scopes
        if requested_scopes_body is not None
        else None
    )

    new_access_token = await services.refresh_access_token(
        db_session, token_str, scopes
    )

    return Token(access_token=new_access_token, token_type="bearer")


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
        key="refresh_token", httponly=True, secure=True, samesite="lax"
    )
