import uuid

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions.app_errors import NotFoundError
from app.semana.models import SemanaParticipant
from app.users.exceptions import CouldNotAssignUsernameError, NoAvailableUsername
from app.users.username.models import Username

MAX_RETRIES = 5


async def assign_username(
    participant_id: uuid.UUID, session: AsyncSession
) -> Username:
    participant = await session.scalar(
        select(SemanaParticipant)
        .where(
            SemanaParticipant.id == participant_id,
            SemanaParticipant.deleted_at.is_(None),
        )
        .options(selectinload(SemanaParticipant.username))
        .with_for_update()
    )
    if participant is None:
        raise NotFoundError("Semana participant not found.")
    if participant.username is not None:
        return participant.username

    for _ in range(MAX_RETRIES):
        available = await session.scalar(
            select(Username)
            .where(
                ~exists().where(
                    SemanaParticipant.semana_id == participant.semana_id,
                    SemanaParticipant.username_id == Username.id,
                ),
            )
            .order_by(Username.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if available is None:
            raise NoAvailableUsername()

        try:
            async with session.begin_nested():
                participant.username = available
                await session.flush()
        except IntegrityError:
            participant.username = None
            continue

        return available

    raise CouldNotAssignUsernameError()
