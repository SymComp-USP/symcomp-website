from fastapi import UploadFile

from app.core.exceptions.app_errors import BadRequestError
from app.core.storage import build_url, delete_file, save_bytes

CHALLENGE_IMAGE_SUBDIR = "challenges"
ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


async def save_challenge_image(file: UploadFile) -> str:
    """
    Valida a política de  challenge e salva a imagem com as funções de core/storage.py.

    Retorna o caminho relativo (ex.: "challenges/<uuid>.jpg").
    """
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise BadRequestError(
            f"Unsupported image type: {file.content_type}. "
            f"Allowed: {sorted(ALLOWED_IMAGE_TYPES)}"
        )

    # Lê com teto para não estourar memória com arquivo gigante
    contents = await file.read(MAX_IMAGE_BYTES + 1)
    if len(contents) > MAX_IMAGE_BYTES:
        raise BadRequestError(f"Image too large (max {MAX_IMAGE_BYTES} bytes).")

    return await save_bytes(
        contents,
        subdir=CHALLENGE_IMAGE_SUBDIR,
        extension=extension,
    )


def delete_challenge_image(image_path: str | None) -> None:
    delete_file(image_path)


def build_challenge_image_url(image_path: str | None) -> str | None:
    return build_url(image_path)
