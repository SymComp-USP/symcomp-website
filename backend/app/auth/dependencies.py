from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import TokenData
from app.auth.scopes import SCOPE_DESCRIPTIONS
from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.core.exceptions.app_errors import UnauthorizedError
from app.users.models import User
from app.users.services import get_deleted_user_by_id, get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login", scopes=SCOPE_DESCRIPTIONS
)


async def get_current_user_including_deleted(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    security_scopes: SecurityScopes,
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """
    Use get_current_user_including_deleted se seu caso de uso não requer que o usuário esteja ativo no banco de dados (isto é, 'deleted_at' pode ser não-nulo)
    """

    SECRET_KEY = settings.secret_key.get_secret_value()
    TOKEN_ALGORITHM = settings.token_algorithm

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = UnauthorizedError(
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        if not payload.get("scopes"):
            raise credentials_exception

        token_scopes = payload.get("scopes").split(" ")
        token_data = TokenData(scopes=token_scopes, user_id=user_id)

    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = await get_user_by_id(db_session, token_data.user_id)

    if user is None:
        user = await get_deleted_user_by_id(db_session, token_data.user_id)

        if user is None:
            raise UnauthorizedError(detail="Inexistent or inactive user")

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise UnauthorizedError(
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_user(
    current_user: Annotated[User, Depends(get_current_user_including_deleted)],
) -> User:
    """
    Use get_current_user se seu caso de uso requer que o usuário esteja ativo no banco de dados ('delete_at' deve ser nulo)
    """

    if current_user.deleted_at is not None:
        raise UnauthorizedError(detail="Inexistent or inactive user")

    return current_user
