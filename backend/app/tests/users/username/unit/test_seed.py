"""Testes do seed do catálogo de usernames."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.username.models import Username, UsernameMother
from app.users.username.seed import (
    read_csv,
    seed_from_csv_files,
    seed_from_rows,
)

# ---------------------------------------------------------------------------
# Dados base
# ---------------------------------------------------------------------------


MOTHERS = [
    {"first_name": "Maria", "last_name": "Silva", "description": "professora"},
    {"first_name": "Ana", "last_name": "Souza", "description": "astronauta"},
]

USERNAMES = [
    {
        "nickname": "MariSilva",
        "first_mome_full_name": "Maria Silva",
        "last_mome_full_name": "Ana Souza",
    },
    {
        "nickname": "AnaSouza",
        "first_mome_full_name": "Ana Souza",
        "last_mome_full_name": "Maria Silva",
    },
]


async def _count(session: AsyncSession, model) -> int:
    return await session.scalar(select(func.count()).select_from(model)) or 0


# ---------------------------------------------------------------------------
# seed_from_rows
# ---------------------------------------------------------------------------


async def test_seed_inserts_all_rows(db_session):
    n_mothers, n_usernames = await seed_from_rows(db_session, MOTHERS, USERNAMES)

    assert n_mothers == 2
    assert n_usernames == 2
    assert await _count(db_session, UsernameMother) == 2
    assert await _count(db_session, Username) == 2


async def test_seed_is_idempotent(db_session):
    first = await seed_from_rows(db_session, MOTHERS, USERNAMES)
    second = await seed_from_rows(db_session, MOTHERS, USERNAMES)

    assert first == (2, 2)
    assert second == (0, 0)  # nada novo na segunda rodada
    assert await _count(db_session, UsernameMother) == 2
    assert await _count(db_session, Username) == 2


async def test_seed_partially_idempotent(db_session):
    """Rodar com um catálogo parcialmente novo só insere o que falta."""
    await seed_from_rows(db_session, MOTHERS, USERNAMES)

    extended_mothers = MOTHERS + [
        {"first_name": "Joana", "last_name": "Lima", "description": "x"}
    ]
    extended_usernames = USERNAMES + [
        {
            "nickname": "JoanaLima",
            "first_mome_full_name": "Joana Lima",
            "last_mome_full_name": "Maria Silva",
        }
    ]

    n_mothers, n_usernames = await seed_from_rows(
        db_session, extended_mothers, extended_usernames
    )

    assert n_mothers == 1
    assert n_usernames == 1
    assert await _count(db_session, UsernameMother) == 3
    assert await _count(db_session, Username) == 3


async def test_seed_raises_on_missing_mother(db_session):
    """Falha ANTES de qualquer INSERT — nada é gravado."""
    bad_usernames = [
        {
            "nickname": "X",
            "first_mome_full_name": "Ninguém Silva",
            "last_mome_full_name": "Maria Silva",
        }
    ]

    with pytest.raises(RuntimeError, match="mothers inexistentes"):
        await seed_from_rows(db_session, MOTHERS, bad_usernames)

    assert await _count(db_session, UsernameMother) == 0
    assert await _count(db_session, Username) == 0


async def test_seed_handles_empty_input(db_session):
    """CSV vazio não deve estourar (insert com [] quebra no SQLAlchemy)."""
    result = await seed_from_rows(db_session, [], [])
    assert result == (0, 0)
    assert await _count(db_session, UsernameMother) == 0
    assert await _count(db_session, Username) == 0


async def test_seed_with_mothers_but_no_usernames(db_session):
    result = await seed_from_rows(db_session, MOTHERS, [])
    assert result == (2, 0)
    assert await _count(db_session, UsernameMother) == 2
    assert await _count(db_session, Username) == 0


async def test_seed_strips_whitespace(db_session):
    mothers = [
        {"first_name": "  Maria  ", "last_name": "  Silva  ", "description": " x "}
    ]
    usernames = [
        {
            "nickname": "  nick  ",
            "first_mome_full_name": "  Maria Silva  ",
            "last_mome_full_name": "  Maria Silva  ",
        }
    ]

    await seed_from_rows(db_session, mothers, usernames)

    m = await db_session.scalar(select(UsernameMother))
    assert m.first_name == "Maria"
    assert m.last_name == "Silva"
    assert m.full_name == "Maria Silva"

    u = await db_session.scalar(select(Username))
    assert u.nickname == "nick"


async def test_seed_dedupes_repeated_mothers(db_session):
    """Mother duplicada no CSV só é inserida uma vez."""
    duplicated = MOTHERS + [MOTHERS[0]]  # Maria Silva aparece 2x

    n_mothers, _ = await seed_from_rows(db_session, duplicated, USERNAMES)

    assert n_mothers == 2
    assert await _count(db_session, UsernameMother) == 2


# ---------------------------------------------------------------------------
# read_csv / seed_from_csv_files
# ---------------------------------------------------------------------------


def test_read_csv(tmp_path):
    path = tmp_path / "x.csv"
    path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

    assert read_csv(path) == [{"a": "1", "b": "2"}, {"a": "3", "b": "4"}]


async def test_seed_from_csv_files_end_to_end(db_session, tmp_path):
    mothers_csv = tmp_path / "mothers.csv"
    mothers_csv.write_text(
        "first_name,last_name,description\nMaria,Silva,prof\nAna,Souza,astro\n",
        encoding="utf-8",
    )
    usernames_csv = tmp_path / "usernames.csv"
    usernames_csv.write_text(
        "nickname,first_mome_full_name,last_mome_full_name\n"
        "MariSilva,Maria Silva,Ana Souza\n",
        encoding="utf-8",
    )

    n_mothers, n_usernames = await seed_from_csv_files(
        db_session, mothers_csv, usernames_csv
    )

    assert (n_mothers, n_usernames) == (2, 1)


async def test_seed_from_csv_files_fails_on_inconsistent_csv(db_session, tmp_path):
    """CSV de usernames referencia mother que não existe no CSV de mothers."""
    mothers_csv = tmp_path / "mothers.csv"
    mothers_csv.write_text(
        "first_name,last_name,description\nMaria,Silva,prof\n",
        encoding="utf-8",
    )
    usernames_csv = tmp_path / "usernames.csv"
    usernames_csv.write_text(
        "nickname,first_mome_full_name,last_mome_full_name\nX,Joana Lima,Maria Silva\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="mothers inexistentes"):
        await seed_from_csv_files(db_session, mothers_csv, usernames_csv)

    # Nada foi inserido
    assert await _count(db_session, UsernameMother) == 0
    assert await _count(db_session, Username) == 0
