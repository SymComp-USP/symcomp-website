"""Testes de integração dos endpoints de imagem do challenge."""

import uuid

import pytest
from httpx import AsyncClient

from app.challenges.services.image import MAX_IMAGE_BYTES


JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 100


def _jpeg() -> tuple[str, bytes, str]:
    return ("photo.jpg", JPEG_BYTES, "image/jpeg")


def _relative_from_url(url: str) -> str:
    """'/media/challenges/x.jpg' -> 'challenges/x.jpg'."""
    return url.removeprefix("/media/")


# ---------------------------------------------------------------------------
# PUT /admin/challenge/{id}/image
# ---------------------------------------------------------------------------


async def test_upload_happy_path_writes_file_and_returns_url(
    db_client: AsyncClient, as_user, admin, challenge, media_root
):
    c = as_user(admin)

    r = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["image_url"].startswith("/media/challenges/")

    absolute = media_root / _relative_from_url(body["image_url"])
    assert absolute.exists()
    assert absolute.read_bytes() == JPEG_BYTES


async def test_upload_replaces_and_deletes_old_file(
    db_client: AsyncClient, as_user, admin, challenge, media_root
):
    c = as_user(admin)

    r1 = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )
    old_abs = media_root / _relative_from_url(r1.json()["image_url"])
    assert old_abs.exists()

    r2 = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )
    new_url = r2.json()["image_url"]

    assert new_url != r1.json()["image_url"]
    assert not old_abs.exists(), "arquivo antigo não foi apagado"
    assert (media_root / _relative_from_url(new_url)).exists()


async def test_upload_non_admin_is_rejected(
    db_client: AsyncClient, as_user, user, challenge
):
    c = as_user(user)
    r = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )
    assert r.status_code in (401, 403)


async def test_upload_challenge_not_found(
    db_client: AsyncClient, as_user, admin, media_root
):
    c = as_user(admin)
    r = await c.put(
        f"/api/v1/admin/challenge/{uuid.uuid4()}/image",
        files={"file": _jpeg()},
    )
    assert r.status_code == 404
    # Nada escrito em disco
    assert not (media_root / "challenges").exists() or not any(
        (media_root / "challenges").iterdir()
    )


async def test_upload_rejects_unsupported_content_type(
    db_client: AsyncClient, as_user, admin, challenge, media_root
):
    c = as_user(admin)
    r = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert r.status_code == 400
    # Nada escrito em disco
    assert not (media_root / "challenges").exists() or not any(
        (media_root / "challenges").iterdir()
    )


async def test_upload_rejects_oversized_file(
    db_client: AsyncClient, as_user, admin, challenge, media_root
):
    big = b"\x00" * (MAX_IMAGE_BYTES + 1)
    c = as_user(admin)
    r = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": ("big.jpg", big, "image/jpeg")},
    )
    assert r.status_code == 400
    assert not (media_root / "challenges").exists() or not any(
        (media_root / "challenges").iterdir()
    )


# ---------------------------------------------------------------------------
# DELETE /admin/challenge/{id}/image
# ---------------------------------------------------------------------------


async def test_delete_removes_file_and_clears_field(
    db_client: AsyncClient, as_user, admin, challenge, media_root
):
    c = as_user(admin)

    r = await c.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )
    absolute = media_root / _relative_from_url(r.json()["image_url"])
    assert absolute.exists()

    r = await c.delete(f"/api/v1/admin/challenge/{challenge.id}/image")
    assert r.status_code == 204
    assert not absolute.exists()

    # Reflete no GET público
    r = await c.get(f"/api/v1/challenge/{challenge.id}")
    assert r.json()["image_url"] is None


async def test_delete_when_no_image_is_noop(
    db_client: AsyncClient, as_user, admin, challenge
):
    c = as_user(admin)
    r = await c.delete(f"/api/v1/admin/challenge/{challenge.id}/image")
    assert r.status_code == 204


async def test_delete_non_admin_is_rejected(
    db_client: AsyncClient, as_user, user, challenge
):
    c = as_user(user)
    r = await c.delete(f"/api/v1/admin/challenge/{challenge.id}/image")
    assert r.status_code in (401, 403)


async def test_delete_challenge_not_found(db_client: AsyncClient, as_user, admin):
    c = as_user(admin)
    r = await c.delete(f"/api/v1/admin/challenge/{uuid.uuid4()}/image")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Exposição em outros endpoints
# ---------------------------------------------------------------------------


async def test_public_challenge_exposes_image_url(
    db_client: AsyncClient, as_user, admin, user, challenge
):
    c_admin = as_user(admin)
    await c_admin.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )

    c_user = as_user(user)
    r = await c_user.get(f"/api/v1/challenge/{challenge.id}")
    assert r.status_code == 200
    assert r.json()["image_url"].startswith("/media/challenges/")


async def test_challenge_without_image_returns_null(
    db_client: AsyncClient, as_user, user, challenge
):
    c = as_user(user)
    r = await c.get(f"/api/v1/challenge/{challenge.id}")
    assert r.status_code == 200
    assert r.json()["image_url"] is None


async def test_list_challenges_includes_image_url(
    db_client: AsyncClient, as_user, admin, user, challenge
):
    c_admin = as_user(admin)
    await c_admin.put(
        f"/api/v1/admin/challenge/{challenge.id}/image",
        files={"file": _jpeg()},
    )

    c_user = as_user(user)
    r = await c_user.get("/api/v1/challenge/")
    assert r.status_code == 200

    items = r.json()["items"]
    ours = next(item for item in items if item["id"] == str(challenge.id))
    assert ours["image_url"].startswith("/media/challenges/")


# ---------------------------------------------------------------------------
# Falha do flush deve limpar o arquivo novo (órfão)
# ---------------------------------------------------------------------------


async def test_upload_cleans_up_new_file_on_db_failure(
    db_client: AsyncClient,
    as_user,
    admin,
    challenge,
    media_root,
    monkeypatch,
):
    """Se o flush falhar, o arquivo novo é apagado para não deixar órfão."""
    from sqlalchemy.ext.asyncio import AsyncSession

    original_flush = AsyncSession.flush

    async def failing_flush(self, *args, **kwargs):
        # Permite flush nas queries de leitura; quebra só no commit da escrita
        raise RuntimeError("boom")

    # Substitui só para esta chamada
    monkeypatch.setattr(AsyncSession, "flush", failing_flush)

    c = as_user(admin)
    with pytest.raises(RuntimeError, match="boom"):
        await c.put(
            f"/api/v1/admin/challenge/{challenge.id}/image",
            files={"file": _jpeg()},
        )

    # Nada escrito
    challenges_dir = media_root / "challenges"
    assert not challenges_dir.exists() or not any(challenges_dir.iterdir())
