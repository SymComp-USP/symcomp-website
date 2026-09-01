import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


async def log_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_in_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_in_ms,
    )

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response.headers.append("X-Request-ID", request_id)

    return response
