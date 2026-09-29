#!/usr/bin/env python3

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import create_database
from app.users.username.seed import seed_from_csv_files

DATA_DIR = Path(__file__).parent / "data"


@asynccontextmanager
async def _session_scope() -> AsyncIterator[AsyncSession]:
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
    async with _session_scope() as session:
        n_mothers, n_usernames = await seed_from_csv_files(
            session,
            DATA_DIR / "mothers.csv",
            DATA_DIR / "usernames.csv",
        )
    print(f"Seed concluído: {n_mothers} mothers, {n_usernames} usernames.")


if __name__ == "__main__":
    asyncio.run(main())
