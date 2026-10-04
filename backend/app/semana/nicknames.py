import csv
import secrets
from functools import lru_cache
from pathlib import Path

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.semana.models import SemanaParticipant

NICKNAME_FILE = Path(__file__).parents[2] / "scripts" / "data" / "usernames.csv"
MAX_GENERATION_ATTEMPTS = 20


@lru_cache(maxsize=1)
def nickname_bases() -> tuple[str, ...]:
    with NICKNAME_FILE.open(encoding="utf-8", newline="") as file:
        bases = tuple(
            row["nickname"].strip()
            for row in csv.DictReader(file)
            if row.get("nickname", "").strip()
        )
    if not bases:
        raise RuntimeError(f"No nickname bases found in {NICKNAME_FILE}")
    return bases


async def generate_nickname(session: AsyncSession, semana_id: int) -> str:
    for _ in range(MAX_GENERATION_ATTEMPTS):
        candidate = f"{secrets.choice(nickname_bases())}{secrets.randbelow(10000):04d}"
        taken = await session.scalar(
            select(
                exists().where(
                    SemanaParticipant.semana_id == semana_id,
                    SemanaParticipant.nickname == candidate,
                )
            )
        )
        if not taken:
            return candidate

    raise RuntimeError("Could not generate a unique Semana nickname.")
