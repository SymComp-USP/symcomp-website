import csv
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from app.core.config import AppEnv, Settings
from app.semana.models import Semana
from scripts import seed_semana_data

TSV_COLUMNS = [
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
]
VALID_ROW = {
    "Título da atividade": "Test activity",
    "Descrição da atividade": "Test description",
    "Tipo de Atividade": "Palestra",
    "Horas": "1",
    "Pontos": "100",
    "Localização": "Auditório",
    "Horário Começo": "06/10/2026 13:00:00",
    "Horário Término": "06/10/2026 14:00:00",
    "Nomes dos palestrantes": "Test Speaker",
    "Arquivos de Imagem": "speaker.jpg",
    "Descrições dos palestrantes": "Test biography",
}


def write_schedule(
    monkeypatch, tmp_path, rows, *, image_files=("speaker.jpg",), columns=None
):
    image_dir = tmp_path / "imagens_palestrantes"
    image_dir.mkdir(exist_ok=True)
    for image_name in image_files:
        image_path = image_dir / image_name
        image_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(b"test image")

    schedule_path = tmp_path / "palestras.tsv"
    fieldnames = columns or TSV_COLUMNS
    with schedule_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    monkeypatch.setattr(seed_semana_data, "SCHEDULE_FILE", schedule_path)
    monkeypatch.setattr(seed_semana_data, "SPEAKER_IMAGES_DIR", image_dir)


def image_signature_matches_extension(path):
    header = path.read_bytes()[:12]
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix == ".webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    return False


def test_load_schedule_reads_activities_and_speaker_photos():
    schedule = seed_semana_data.load_schedule()

    assert len(schedule) == 17
    speakers = [speaker for item in schedule for speaker in item["speakers"]]
    assert len(speakers) == 20
    assert all(
        speaker["nome"].strip() and speaker["sobre"].strip() for speaker in speakers
    )
    assert all(speaker["image_path"].is_file() for speaker in speakers)
    assert all(
        speaker["image_path"].suffix.lower()
        in seed_semana_data.SUPPORTED_IMAGE_EXTENSIONS
        for speaker in speakers
    )
    assert all(
        0 < speaker["image_path"].stat().st_size <= seed_semana_data.MAX_IMAGE_BYTES
        for speaker in speakers
    )
    image_paths = [speaker["image_path"].resolve() for speaker in speakers]
    assert all(image_signature_matches_extension(path) for path in image_paths)
    assert len(image_paths) == len(set(image_paths))
    referenced_images = set(image_paths)
    supported_files = {
        path.resolve()
        for path in seed_semana_data.SPEAKER_IMAGES_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in seed_semana_data.SUPPORTED_IMAGE_EXTENSIONS
    }
    assert referenced_images == supported_files

    tako_activity = next(
        item for item in schedule if item["titulo"].startswith("Como a Tako")
    )
    tako_images = {
        speaker["nome"]: speaker["image_path"].name
        for speaker in tako_activity["speakers"]
    }
    assert tako_images == {
        "Bruno Cerejo": "bruno-cerejo.jpeg",
        "André Spanguero": "andre-spanguero.jpg",
    }


def test_schedule_rows_are_unique_valid_and_non_overlapping_by_location():
    schedule = seed_semana_data.load_schedule()
    titles = [item["titulo"] for item in schedule]

    assert all(title and len(title) <= 255 for title in titles)
    assert len(titles) == len(set(titles))
    for item in schedule:
        assert item["comeca_as"].tzinfo == ZoneInfo("America/Sao_Paulo")
        assert item["comeca_as"].year == item["termina_as"].year == 2026
        assert item["comeca_as"].month == item["termina_as"].month == 10
        assert 5 <= item["comeca_as"].day <= 9
        assert item["termina_as"] > item["comeca_as"]
        assert item["horas"] >= 1
        assert item["pontos"] >= 0
        assert item["descricao"] is None or len(item["descricao"]) <= 5000
        assert item["local"] is None or len(item["local"]) <= 255

    for index, first in enumerate(schedule):
        for second in schedule[index + 1 :]:
            if first["local"] and first["local"] == second["local"]:
                assert (
                    first["termina_as"] <= second["comeca_as"]
                    or second["termina_as"] <= first["comeca_as"]
                ), (first["titulo"], second["titulo"])


@pytest.mark.parametrize(
    ("overrides", "images", "message"),
    [
        (
            {
                "Nomes dos palestrantes": "Speaker One|Speaker Two",
                "Descrições dos palestrantes": "Bio one|Bio two",
            },
            ("speaker.jpg",),
            "Speaker columns have different counts",
        ),
        ({"Arquivos de Imagem": ""}, (), "Speaker image is missing"),
        (
            {"Descrições dos palestrantes": ""},
            ("speaker.jpg",),
            "Speaker bio is missing",
        ),
        ({"Nomes dos palestrantes": ""}, ("speaker.jpg",), "Speaker name is missing"),
        (
            {"Arquivos de Imagem": "speaker.heic"},
            ("speaker.heic",),
            "Unsupported speaker image type",
        ),
        ({"Arquivos de Imagem": "missing.jpg"}, (), "Speaker image not found"),
        ({"Arquivos de Imagem": "../speaker.jpg"}, (), "Invalid speaker image path"),
    ],
)
def test_load_schedule_rejects_invalid_speaker_data(
    monkeypatch, tmp_path, overrides, images, message
):
    row = {**VALID_ROW, **overrides}
    write_schedule(monkeypatch, tmp_path, [row], image_files=images)

    with pytest.raises((ValueError, FileNotFoundError), match=message):
        seed_semana_data.load_schedule()


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"Tipo de Atividade": "Coffee break"}, "Invalid title or activity type"),
        ({"Horário Término": "06/10/2026 13:00:00"}, "Invalid schedule"),
        ({"Horário Começo": "06/10/2025 13:00:00"}, "outside the 2026 event"),
        ({"Horas": "0"}, "Invalid hours or points"),
        ({"Pontos": "-1"}, "Invalid hours or points"),
        ({"Pontos": "one hundred"}, "Invalid date or numeric value"),
        ({"Título da atividade": "T" * 256}, "Activity title is too long"),
        ({"Descrição da atividade": "D" * 5001}, "Description is too long"),
        ({"Localização": "L" * 256}, "Location is too long"),
    ],
)
def test_load_schedule_rejects_invalid_activity_fields(
    monkeypatch, tmp_path, overrides, message
):
    write_schedule(monkeypatch, tmp_path, [{**VALID_ROW, **overrides}])

    with pytest.raises(ValueError, match=message):
        seed_semana_data.load_schedule()


def test_load_schedule_rejects_duplicate_titles(monkeypatch, tmp_path):
    write_schedule(monkeypatch, tmp_path, [VALID_ROW, VALID_ROW])

    with pytest.raises(ValueError, match="Duplicate activity title"):
        seed_semana_data.load_schedule()


def test_load_schedule_rejects_missing_columns(monkeypatch, tmp_path):
    columns = TSV_COLUMNS[:-1]
    row = {key: value for key, value in VALID_ROW.items() if key in columns}
    write_schedule(monkeypatch, tmp_path, [row], columns=columns)

    with pytest.raises(ValueError, match="Unexpected columns"):
        seed_semana_data.load_schedule()


def test_load_schedule_rejects_duplicate_columns(monkeypatch, tmp_path):
    columns = [*TSV_COLUMNS, "Título da atividade"]
    write_schedule(monkeypatch, tmp_path, [VALID_ROW], columns=columns)

    with pytest.raises(ValueError, match="Duplicate columns"):
        seed_semana_data.load_schedule()


@pytest.mark.parametrize("row_width", [len(TSV_COLUMNS) - 1, len(TSV_COLUMNS) + 1])
def test_load_schedule_rejects_malformed_row_width(monkeypatch, tmp_path, row_width):
    image_dir = tmp_path / "imagens_palestrantes"
    image_dir.mkdir()
    (image_dir / "speaker.jpg").write_bytes(b"test image")
    schedule_path = tmp_path / "palestras.tsv"
    values = [VALID_ROW[column] for column in TSV_COLUMNS]
    values = values[:row_width] if row_width < len(values) else [*values, "unexpected"]
    with schedule_path.open("w", encoding="utf-8", newline="") as file:
        file.write("\t".join(TSV_COLUMNS) + "\n")
        file.write("\t".join(values) + "\n")

    monkeypatch.setattr(seed_semana_data, "SCHEDULE_FILE", schedule_path)
    monkeypatch.setattr(seed_semana_data, "SPEAKER_IMAGES_DIR", image_dir)

    with pytest.raises(ValueError, match="Invalid number of columns"):
        seed_semana_data.load_schedule()


def test_load_schedule_rejects_oversized_image(monkeypatch, tmp_path):
    write_schedule(monkeypatch, tmp_path, [VALID_ROW])
    image_path = seed_semana_data.SPEAKER_IMAGES_DIR / "speaker.jpg"
    image_path.write_bytes(b"x" * (seed_semana_data.MAX_IMAGE_BYTES + 1))

    with pytest.raises(ValueError, match="invalid size"):
        seed_semana_data.load_schedule()


def test_load_schedule_rejects_empty_file(monkeypatch, tmp_path):
    write_schedule(monkeypatch, tmp_path, [])

    with pytest.raises(ValueError, match="No activities found"):
        seed_semana_data.load_schedule()


@pytest.mark.asyncio
async def test_main_runs_in_production_and_is_additive_on_repeated_runs(
    monkeypatch, tmp_path
):
    event_state = {"event": Semana(id=2026, nome="Edited event name", ano=2026)}
    manually_edited = SimpleNamespace(titulo="Existing activity", descricao="Edited")
    activities = [manually_edited]
    created = []
    saved_images = []
    image_path = tmp_path / "speaker.jpg"
    image_path.write_bytes(b"test image")
    seed_item = {
        "titulo": "New activity",
        "tipo": seed_semana_data.TipoAtividade.PALESTRA,
        "descricao": "Initial description",
        "local": "Auditorium",
        "comeca_as": datetime(2026, 10, 6, 10, tzinfo=UTC),
        "termina_as": datetime(2026, 10, 6, 11, tzinfo=UTC),
        "pontos": 100,
        "horas": 1,
        "speakers": [{"nome": "Speaker", "sobre": "Bio", "image_path": image_path}],
    }
    existing_seed_item = {
        **seed_item,
        "titulo": "Existing activity",
        "descricao": "Do not overwrite this",
    }

    class FakeSession:
        def add(self, value):
            event_state["event"] = value

        async def flush(self):
            pass

        async def scalar(self, _statement):
            return event_state["event"]

        async def scalars(self, _statement):
            return SimpleNamespace(all=lambda: list(activities))

    session = FakeSession()

    @asynccontextmanager
    async def fake_session_scope(_settings):
        yield session

    async def fake_save_bytes(contents, *, subdir, extension):
        saved_images.append((contents, subdir, extension))
        return "palestrantes/speaker.jpg"

    async def fake_create_atividade(_session, _event, **fields):
        activity = SimpleNamespace(
            titulo=fields["titulo"],
            descricao=fields["descricao"],
            palestrantes=fields["palestrantes"],
        )
        activities.append(activity)
        created.append(activity)
        return activity

    monkeypatch.setattr(
        seed_semana_data, "get_settings", lambda: Settings(app_env=AppEnv.production)
    )
    monkeypatch.setattr(
        seed_semana_data,
        "load_schedule",
        lambda: [existing_seed_item, seed_item],
    )
    monkeypatch.setattr(seed_semana_data, "session_scope", fake_session_scope)
    monkeypatch.setattr(seed_semana_data, "save_bytes", fake_save_bytes)
    monkeypatch.setattr(seed_semana_data, "create_atividade", fake_create_atividade)

    await seed_semana_data.main()
    await seed_semana_data.main()

    assert len(created) == 1
    assert manually_edited.descricao == "Edited"
    assert len(activities) == 2
    assert event_state["event"].nome == "Edited event name"
    assert event_state["event"].ano == 2026
    assert created[0].palestrantes == [
        {
            "nome": "Speaker",
            "sobre": "Bio",
            "foto": "/media/palestrantes/speaker.jpg",
        }
    ]
    assert saved_images == [(b"test image", "palestrantes", "jpg")]


@pytest.mark.asyncio
async def test_main_deletes_saved_media_when_activity_creation_fails(
    monkeypatch, tmp_path
):
    event = Semana(id=2026, nome="Semana da Computação", ano=2026)
    image_path = tmp_path / "speaker.jpg"
    image_path.write_bytes(b"test image")
    item = {
        "titulo": "Activity",
        "descricao": "Description",
        "tipo": seed_semana_data.TipoAtividade.PALESTRA,
        "local": "Auditorium",
        "comeca_as": datetime(2026, 10, 6, 10, tzinfo=UTC),
        "termina_as": datetime(2026, 10, 6, 11, tzinfo=UTC),
        "pontos": 100,
        "horas": 1,
        "speakers": [{"nome": "Speaker", "sobre": "Bio", "image_path": image_path}],
    }
    session = SimpleNamespace(
        scalar=lambda _statement: None,
        scalars=lambda _statement: None,
    )

    async def scalar(_statement):
        return event

    async def scalars(_statement):
        return SimpleNamespace(all=list)

    session.scalar = scalar
    session.scalars = scalars
    deleted_media = []

    @asynccontextmanager
    async def fake_session_scope(_settings):
        yield session

    async def fake_save_bytes(_contents, *, subdir, extension):
        return f"{subdir}/new.{extension}"

    async def fail_create_atividade(_session, _event, **_fields):
        raise RuntimeError("database write failed")

    monkeypatch.setattr(
        seed_semana_data, "get_settings", lambda: Settings(app_env=AppEnv.production)
    )
    monkeypatch.setattr(seed_semana_data, "load_schedule", lambda: [item])
    monkeypatch.setattr(seed_semana_data, "session_scope", fake_session_scope)
    monkeypatch.setattr(seed_semana_data, "save_bytes", fake_save_bytes)
    monkeypatch.setattr(seed_semana_data, "create_atividade", fail_create_atividade)
    monkeypatch.setattr(seed_semana_data, "delete_file", deleted_media.append)

    with pytest.raises(RuntimeError, match="database write failed"):
        await seed_semana_data.main()

    assert deleted_media == ["palestrantes/new.jpg"]


@pytest.mark.asyncio
async def test_main_creates_missing_event_in_production(monkeypatch):
    event_state = {"event": None}

    class FakeSession:
        def add(self, value):
            event_state["event"] = value

        async def flush(self):
            pass

        async def scalar(self, _statement):
            return event_state["event"]

        async def scalars(self, _statement):
            return SimpleNamespace(all=list)

    @asynccontextmanager
    async def fake_session_scope(_settings):
        yield FakeSession()

    monkeypatch.setattr(
        seed_semana_data, "get_settings", lambda: Settings(app_env=AppEnv.production)
    )
    monkeypatch.setattr(seed_semana_data, "load_schedule", list)
    monkeypatch.setattr(seed_semana_data, "session_scope", fake_session_scope)

    await seed_semana_data.main()

    assert event_state["event"].nome == "Semana da Computação 2026"
    assert event_state["event"].ano == 2026
