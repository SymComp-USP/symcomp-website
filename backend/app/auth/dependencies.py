from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import TokenData
from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.core.exceptions.app_errors import BadRequestError, UnauthorizedError
from app.users.models import User
from app.users.services import get_deleted_user_by_email, get_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Use get_current_user se seu caso de uso não requer que o usuário esteja ativo
# no banco de dados ('delete_at' pode ser não-nulo)


async def get_current_user(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    SECRET_KEY = settings.secret_key.get_secret_value()
    TOKEN_ALGORITHM = settings.token_algorithm

    credentials_exception = UnauthorizedError(detail="Could not validate credentials")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(db_session, token_data.username)

    if user is None:
        user = await get_deleted_user_by_email(db_session, token_data.username)

        if user is None:
            raise credentials_exception

    return user


# Use get_current_active_user se seu caso de uso requer que o usuário esteja ativo
# no banco de dados (isto é, 'deleted_at' deve ser nulo)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.deleted_at is not None:
        raise BadRequestError(detail="Inactive user")

    return current_user
