import uuid

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.app_errors import NotFoundError
from app.users.exceptions import CouldNotAssignUsernameError, NoAvailableUsername
from app.users.models import User
from app.users.username.models import Username

MAX_RETRIES = 5


async def assign_username(user_id: uuid.UUID, session: AsyncSession) -> Username:
    user = await session.scalar(
        select(User)
        .where(User.id == user_id, User.deleted_at.is_(None))
        .options(selectinload(User.username))
        .execution_options(populate_existing=True)
        .with_for_update()
    )
    if user is None:
        raise NotFoundError("User not found.")
    if user.username is not None:
        return user.username

    for _ in range(MAX_RETRIES):
        available = await session.scalar(
            select(Username)
            .where(
                ~exists().where(User.username_id == Username.id),
            )
            .order_by(Username.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if available is None:
            raise NoAvailableUsername()

        try:
            async with session.begin_nested():
                user.username = available
                await session.flush()
        except IntegrityError:
            user.username = None
            continue

        return available

    raise CouldNotAssignUsernameError()
