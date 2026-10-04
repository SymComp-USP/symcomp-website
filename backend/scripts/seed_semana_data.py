"""Seed the initial Semana da Computacao 2026 schedule.

Run from ``backend/`` with ``uv run python scripts/seed_semana_data.py`` after
configuring the environment for the intended database.
Existing events and activities are left unchanged; only missing records are added.
Activity details are read from ``scripts/data/palestras.tsv`` and speaker images
from ``scripts/data/imagens_palestrantes``.
"""

import asyncio
import csv
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from importlib import import_module
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.atividade.image import MAX_IMAGE_BYTES
from app.atividade.models import Atividade, StatusAtividade, TipoAtividade
from app.atividade.services import create_atividade
from app.core.config import Settings, get_settings
from app.core.database import create_database
from app.core.storage import delete_file, save_bytes
from app.semana.models import Semana

import_module("app.challenges.models.challenge")
import_module("app.users.models")

DATA_DIR = Path(__file__).resolve().parent / "data"
SCHEDULE_FILE = DATA_DIR / "palestras.tsv"
SPEAKER_IMAGES_DIR = DATA_DIR / "imagens_palestrantes"
LOCAL_TIMEZONE = ZoneInfo("America/Sao_Paulo")
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

ACTIVITY_TYPES = {
    "Palestra": TipoAtividade.PALESTRA,
    "Workshop": TipoAtividade.WORKSHOP,
    "Encerramento": TipoAtividade.ENCERRAMENTO,
    "Conversa": TipoAtividade.CONVERSA,
}


@asynccontextmanager
async def session_scope(settings: Settings) -> AsyncGenerator[AsyncSession, None]:
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


def load_schedule() -> list[dict]:
    required_columns = {
        "Título da atividade",
        "Descrição da atividade",
        "Tipo de Atividade",
        "Horas",
        "Pontos",
        "Localização",
        "Horário Começo",
        "Horário Término",
        "Nomes dos palestrantes",
        "Arquivos de Imagem",
        "Descrições dos palestrantes",
    }
    with SCHEDULE_FILE.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        if reader.fieldnames is None or not required_columns.issubset(
            reader.fieldnames
        ):
            raise ValueError(f"Unexpected columns in {SCHEDULE_FILE}.")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError(f"Duplicate columns in {SCHEDULE_FILE}.")

        schedule = []
        seen_titles = set()
        for line_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(
                    f"Invalid number of columns on TSV line {line_number}."
                )

            title = row["Título da atividade"].strip()
            activity_type = ACTIVITY_TYPES.get(row["Tipo de Atividade"].strip())
            if not title or activity_type is None:
                raise ValueError(
                    f"Invalid title or activity type on TSV line {line_number}."
                )
            if title in seen_titles:
                raise ValueError(f"Duplicate activity title on TSV line {line_number}.")
            if len(title) > 255:
                raise ValueError(
                    f"Activity title is too long on TSV line {line_number}."
                )

            description = row["Descrição da atividade"].strip() or None
            location = row["Localização"].strip() or None
            if description is not None and len(description) > 5000:
                raise ValueError(f"Description is too long on TSV line {line_number}.")
            if location is not None and len(location) > 255:
                raise ValueError(f"Location is too long on TSV line {line_number}.")

            try:
                starts_at = datetime.strptime(
                    row["Horário Começo"].strip(), "%d/%m/%Y %H:%M:%S"
                ).replace(tzinfo=LOCAL_TIMEZONE)
                ends_at = datetime.strptime(
                    row["Horário Término"].strip(), "%d/%m/%Y %H:%M:%S"
                ).replace(tzinfo=LOCAL_TIMEZONE)
                hours = int(row["Horas"])
                points = int(row["Pontos"])
            except ValueError as error:
                raise ValueError(
                    f"Invalid date or numeric value on TSV line {line_number}."
                ) from error
            if ends_at <= starts_at:
                raise ValueError(f"Invalid schedule on TSV line {line_number}.")
            if starts_at.year != 2026 or ends_at.year != 2026:
                raise ValueError(
                    f"Schedule is outside the 2026 event on TSV line {line_number}."
                )
            if hours < 1 or points < 0:
                raise ValueError(f"Invalid hours or points on TSV line {line_number}.")

            speakers = []
            speaker_fields = [
                [value.strip() for value in row[field].split("|")]
                for field in (
                    "Nomes dos palestrantes",
                    "Arquivos de Imagem",
                    "Descrições dos palestrantes",
                )
            ]
            if len({len(values) for values in speaker_fields}) != 1:
                raise ValueError(
                    f"Speaker columns have different counts on TSV line {line_number}."
                )

            for speaker_number, (name, image_name, bio) in enumerate(
                zip(*speaker_fields, strict=True), start=1
            ):
                name, image_name, bio = name.strip(), image_name.strip(), bio.strip()
                if not any((name, image_name, bio)):
                    continue
                if not name:
                    raise ValueError(
                        f"Speaker name is missing on TSV line {line_number}, "
                        f"speaker {speaker_number}."
                    )
                if not image_name:
                    raise ValueError(
                        f"Speaker image is missing on TSV line {line_number}, "
                        f"speaker {speaker_number}."
                    )
                if not bio:
                    raise ValueError(
                        f"Speaker bio is missing on TSV line {line_number}, "
                        f"speaker {speaker_number}."
                    )
                if Path(image_name).name != image_name or "\\" in image_name:
                    raise ValueError(
                        f"Invalid speaker image path on TSV line {line_number}."
                    )

                image_path = SPEAKER_IMAGES_DIR / image_name if image_name else None
                if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                    raise ValueError(
                        f"Unsupported speaker image type on TSV line {line_number}: "
                        f"{image_path.suffix}"
                    )
                if not image_path.is_file():
                    raise FileNotFoundError(
                        f"Speaker image not found on TSV line {line_number}: {image_path}"
                    )
                if not 0 < image_path.stat().st_size <= MAX_IMAGE_BYTES:
                    raise ValueError(
                        f"Speaker image has an invalid size on TSV line {line_number}: "
                        f"{image_path}"
                    )
                speakers.append({"nome": name, "sobre": bio, "image_path": image_path})

            schedule.append(
                {
                    "tipo": activity_type,
                    "titulo": title,
                    "descricao": description,
                    "local": location,
                    "speakers": speakers,
                    "comeca_as": starts_at,
                    "termina_as": ends_at,
                    "pontos": points,
                    "horas": hours,
                }
            )
            seen_titles.add(title)
        if not schedule:
            raise ValueError(f"No activities found in {SCHEDULE_FILE}.")
    return schedule


async def main() -> None:
    settings = get_settings()
    schedule = load_schedule()
    stored_images = []
    created_count = 0
    skipped_count = 0
    try:
        async with session_scope(settings) as session:
            event = await session.scalar(select(Semana).where(Semana.ano == 2026))
            if event is None:
                event = Semana(nome="Semana da Computação 2026", ano=2026)
                session.add(event)
                await session.flush()

            activities = await session.scalars(
                select(Atividade).where(Atividade.semana_id == event.id)
            )
            existing_titles = {activity.titulo for activity in activities.all()}

            for item in schedule:
                if item["titulo"] in existing_titles:
                    skipped_count += 1
                    continue

                speakers = []
                for speaker in item["speakers"]:
                    speaker_data = {
                        "nome": speaker["nome"],
                        "sobre": speaker["sobre"],
                    }
                    image_path = speaker["image_path"]
                    if image_path is not None:
                        extension = image_path.suffix.lstrip(".").lower()
                        relative_path = await save_bytes(
                            image_path.read_bytes(),
                            subdir="palestrantes",
                            extension=extension,
                        )
                        stored_images.append(relative_path)
                        speaker_data["foto"] = f"/media/{relative_path}"
                    speakers.append(speaker_data)

                activity_fields = {
                    key: value for key, value in item.items() if key != "speakers"
                }
                await create_atividade(
                    session,
                    event,
                    **activity_fields,
                    palestrantes=speakers,
                    link_live=None,
                    status=StatusAtividade.CONFIRMADA,
                )
                existing_titles.add(item["titulo"])
                created_count += 1
    except Exception:
        for relative_path in stored_images:
            delete_file(relative_path)
        raise

    print(f"Semana: {event.id} ({event.nome} {event.ano})")
    print(
        f"Activities created: {created_count}; "
        f"existing activities skipped: {skipped_count}."
    )


if __name__ == "__main__":
    asyncio.run(main())
