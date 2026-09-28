"""Testes unitários do serviço de imagem do challenge."""

from io import BytesIO

import pytest
from starlette.datastructures import Headers, UploadFile

from app.challenges.services.image import (
    MAX_IMAGE_BYTES,
    build_challenge_image_url,
    delete_challenge_image,
    save_challenge_image,
)
from app.core.exceptions.app_errors import BadRequestError

JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def _upload(
    content: bytes,
    content_type: str | None = "image/jpeg",
    filename: str = "test.jpg",
) -> UploadFile:
    headers = Headers({"content-type": content_type}) if content_type else Headers()
    return UploadFile(
        file=BytesIO(content),
        size=len(content),
        filename=filename,
        headers=headers,
    )


# ---------------------------------------------------------------------------
# save_challenge_image
# ---------------------------------------------------------------------------


async def test_save_jpeg_writes_file_and_returns_relative_path(media_root):
    path = await save_challenge_image(_upload(JPEG_BYTES))

    assert path.startswith("challenges/")
    assert path.endswith(".jpg")
    absolute = media_root / path
    assert absolute.exists()
    assert absolute.read_bytes() == JPEG_BYTES


@pytest.mark.parametrize(
    "content_type,filename,expected_ext",
    [
        ("image/jpeg", "x.jpg", ".jpg"),
        ("image/png", "x.png", ".png"),
        ("image/webp", "x.webp", ".webp"),
    ],
)
async def test_save_accepts_all_allowed_types(
    media_root, content_type, filename, expected_ext
):
    path = await save_challenge_image(
        _upload(JPEG_BYTES, content_type=content_type, filename=filename)
    )
    assert path.endswith(expected_ext)


async def test_save_rejects_unsupported_content_type(media_root):
    with pytest.raises(BadRequestError, match="Unsupported image type"):
        await save_challenge_image(_upload(JPEG_BYTES, content_type="application/pdf"))
    # Não deve ter sobrado nada em disco
    assert not any(media_root.rglob("*")) or all(
        p.is_dir() for p in media_root.rglob("*")
    )


async def test_save_rejects_missing_content_type(media_root):
    with pytest.raises(BadRequestError, match="Unsupported image type"):
        await save_challenge_image(_upload(JPEG_BYTES, content_type=None))


async def test_save_rejects_file_above_max_size(media_root):
    oversized = b"\x00" * (MAX_IMAGE_BYTES + 1)
    with pytest.raises(BadRequestError, match="Image too large"):
        await save_challenge_image(_upload(oversized))


async def test_save_accepts_file_at_exact_max_size(media_root):
    exact = b"\x00" * MAX_IMAGE_BYTES
    path = await save_challenge_image(_upload(exact))
    assert (media_root / path).exists()


async def test_save_generates_unique_filenames(media_root):
    p1 = await save_challenge_image(_upload(JPEG_BYTES))
    p2 = await save_challenge_image(_upload(JPEG_BYTES))

    assert p1 != p2
    assert (media_root / p1).exists()
    assert (media_root / p2).exists()


async def test_save_creates_subdir_if_missing(media_root):
    # media_root existe (tmp_path), mas challenges/ não
    assert not (media_root / "challenges").exists()

    await save_challenge_image(_upload(JPEG_BYTES))

    assert (media_root / "challenges").is_dir()


# ---------------------------------------------------------------------------
# delete_challenge_image
# ---------------------------------------------------------------------------


async def test_delete_removes_file(media_root):
    path = await save_challenge_image(_upload(JPEG_BYTES))
    absolute = media_root / path
    assert absolute.exists()

    delete_challenge_image(path)

    assert not absolute.exists()


def test_delete_none_is_noop(media_root):
    delete_challenge_image(None)  # não deve estourar


def test_delete_missing_file_is_noop(media_root):
    delete_challenge_image("challenges/does-not-exist.jpg")  # noop


# ---------------------------------------------------------------------------
# build_challenge_image_url
# ---------------------------------------------------------------------------


def test_build_url_none_returns_none(media_root):
    assert build_challenge_image_url(None) is None


def test_build_url_joins_prefix(media_root):
    url = build_challenge_image_url("challenges/abc.jpg")
    assert url == "/media/challenges/abc.jpg"


def test_build_url_prefix_without_leading_slash(media_root, monkeypatch):
    from app.core import config

    settings = config.get_settings()
    monkeypatch.setattr(settings, "media_url_prefix", "media")

    url = build_challenge_image_url("challenges/abc.jpg")
    assert url == "media/challenges/abc.jpg"
