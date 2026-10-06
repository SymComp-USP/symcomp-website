from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import email as email_service
from app.auth import services as auth_services
from app.auth.dependencies import get_current_user
from app.auth.models import AuthTokenPurpose
from app.auth.scopes import Scope
from app.core.database import get_session
from app.core.exceptions.app_errors import UnauthorizedError
from app.users import services
from app.users.models import User
from app.users.schemas import UserCreate, UserMe, UserNameUpdate, UserRead, UserUpdate

router = APIRouter(tags=["user"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def signup_with_password(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    user_info: UserCreate,
    mailer: Annotated[
        email_service.EmailService, Depends(email_service.get_email_service)
    ],
):
    user = await services.create_user(db_session, user_info)
    token = await auth_services.create_auth_token(
        db_session, user.id, AuthTokenPurpose.VERIFY_EMAIL, timedelta(hours=24)
    )
    await mailer.send_verification_email(user.email, user.name, token)

    return user


@router.patch("/me", response_model=UserMe)
async def update_my_name(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
    user_in: UserNameUpdate,
):
    """Altera o nome do usuário autenticado. O e-mail não pode ser alterado aqui."""
    await services.update_user(db_session, current_user, UserUpdate(name=user_in.name))
    await db_session.commit()

    user = await services.get_user_profile_by_id(db_session, current_user.id)
    if user is None:
        raise UnauthorizedError(detail="Inexistent or inactive user")
    return user
