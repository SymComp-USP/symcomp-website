"""Seed the minimum data needed to exercise the local Semana flows."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.core.config import get_settings
from app.core.database import create_database
from app.semana.models import SemanaEvent
from app.users.username.seed import seed_from_csv_files
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

DATA_DIR = Path(__file__).parent / "data"


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    settings = get_settings()
    engine, session_factory = create_database(settings)
    try:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        await engine.dispose()


async def main() -> None:
    async with session_scope() as session:
        await seed_from_csv_files(
            session,
            DATA_DIR / "mothers.csv",
            DATA_DIR / "usernames.csv",
        )

        event = await session.scalar(select(SemanaEvent).where(SemanaEvent.ano == 2026))
        if event is None:
            event = SemanaEvent(nome="Semana da Computação", ano=2026)
            session.add(event)
            await session.flush()

        challenge = await session.scalar(
            select(Challenge).where(
                Challenge.semana_id == event.id,
                Challenge.title == "Desafio de boas-vindas",
                Challenge.deleted_at.is_(None),
            )
        )
        if challenge is None:
            challenge = Challenge(
                title="Desafio de boas-vindas",
                prompt="Digite a palavra-chave apresentada na página do evento.",
                scoring_type=ChallengeScoringType.INPUT,
                finishes_at=datetime.now(UTC) + timedelta(days=30),
                points_value=100,
                input_answer="symcomp",
                semana_id=event.id,
            )
            session.add(challenge)
            await session.flush()

        print(f"Semana: {event.id} ({event.nome} {event.ano})")
        print(f"Challenge: {challenge.id} ({challenge.title})")
        print("Resposta do desafio de boas-vindas: symcomp")


if __name__ == "__main__":
    asyncio.run(main())
