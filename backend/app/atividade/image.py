from fastapi import UploadFile

from app.core.exceptions.app_errors import BadRequestError
from app.core.storage import save_bytes

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


async def save_palestrante_photo(file: UploadFile) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise BadRequestError(
            f"Unsupported image type: {file.content_type}. "
            f"Allowed: {sorted(ALLOWED_IMAGE_TYPES)}"
        )

    contents = await file.read(MAX_IMAGE_BYTES + 1)
    if len(contents) > MAX_IMAGE_BYTES:
        raise BadRequestError(f"Image too large (max {MAX_IMAGE_BYTES} bytes).")

    return f"/media/{await save_bytes(contents, subdir='palestrantes', extension=extension)}"
