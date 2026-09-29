"""Seed the username catalog from CSV files or tabular data."""

from __future__ import annotations

import csv
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.username.models import Username, UsernameMother


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _mother_full_name(row: dict) -> str:
    return f"{row['first_name'].strip()} {row['last_name'].strip()}"


def _to_mother_values(row: dict) -> dict:
    first = row["first_name"].strip()
    last = row["last_name"].strip()
    return {
        "id": uuid4(),
        "first_name": first,
        "last_name": last,
        "full_name": f"{first} {last}",
        "description": row["description"].strip(),
    }


def _to_username_values(row: dict, mother_ids: dict[str, UUID]) -> dict:
    return {
        "id": uuid4(),
        "nickname": row["nickname"].strip(),
        "first_mother_id": mother_ids[row["first_mome_full_name"].strip()],
        "last_mother_id": mother_ids[row["last_mome_full_name"].strip()],
    }


def _validate_refs(username_rows: list[dict], mother_names: set[str]) -> None:
    missing: list[tuple[str, str, str]] = []
    for row in username_rows:
        first = row["first_mome_full_name"].strip()
        last = row["last_mome_full_name"].strip()
        if first not in mother_names or last not in mother_names:
            missing.append((row["nickname"].strip(), first, last))

    if missing:
        raise RuntimeError(
            f"{len(missing)} usernames referenciam mothers inexistentes. "
            f"Exemplos: {missing[:5]}"
        )


async def _insert_mothers(
    session: AsyncSession, mother_rows: list[dict]
) -> tuple[dict[str, UUID], int]:
    if not mother_rows:
        return {}, 0

    statement = (
        insert(UsernameMother)
        .values([_to_mother_values(row) for row in mother_rows])
        .on_conflict_do_nothing(index_elements=["full_name"])
        .returning(UsernameMother.id)
    )
    result = await session.execute(statement)
    inserted_count = len(result.scalars().all())
    mothers = await session.scalars(select(UsernameMother))
    mother_ids = {mother.full_name: mother.id for mother in mothers}
    return mother_ids, inserted_count


async def _insert_usernames(
    session: AsyncSession,
    username_rows: list[dict],
    mother_ids: dict[str, UUID],
) -> int:
    if not username_rows:
        return 0

    statement = (
        insert(Username)
        .values([_to_username_values(row, mother_ids) for row in username_rows])
        .on_conflict_do_nothing(index_elements=["nickname"])
        .returning(Username.id)
    )
    result = await session.execute(statement)
    return len(result.scalars().all())


async def seed_from_rows(
    session: AsyncSession,
    mother_rows: list[dict],
    username_rows: list[dict],
) -> tuple[int, int]:
    async with session.begin_nested():
        mother_names = {_mother_full_name(row) for row in mother_rows}
        _validate_refs(username_rows, mother_names)
        mother_ids, inserted_mothers = await _insert_mothers(session, mother_rows)
        inserted_usernames = await _insert_usernames(session, username_rows, mother_ids)
    return inserted_mothers, inserted_usernames


async def seed_from_csv_files(
    session: AsyncSession,
    mothers_path: Path,
    usernames_path: Path,
) -> tuple[int, int]:
    return await seed_from_rows(
        session,
        read_csv(mothers_path),
        read_csv(usernames_path),
    )
