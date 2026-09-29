import asyncio
import uuid
from pathlib import Path

from app.core.config import get_settings


async def save_bytes(
    contents: bytes,
    *,
    subdir: str,
    extension: str,
) -> str:
    """
    Salva bytes em media_root/<subdir>/<uuid>.<ext>. Retorna caminho relativo.

    Não realiza validações de arquivo — quem chama deve decidir a política.
    """
    settings = get_settings()
    relative = Path(subdir) / f"{uuid.uuid4()}.{extension}"
    absolute = settings.media_root / relative
    absolute.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(absolute.write_bytes, contents)
    return str(relative)


def delete_file(relative_path: str | None) -> None:
    """Apaga o arquivo. Retorna imediatamente se None ou se não existir."""
    if not relative_path:
        return
    settings = get_settings()
    (settings.media_root / relative_path).unlink(missing_ok=True)


def build_url(relative_path: str | None) -> str | None:
    if relative_path is None:
        return None
    settings = get_settings()
    return f"{settings.media_url_prefix.rstrip('/')}/{relative_path}"
