from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable
from re import fullmatch
from typing import ClassVar

from fastapi import Request
from fastapi.responses import JSONResponse

RateLimit = tuple[int, int]

LIMITS: dict[tuple[str, str], RateLimit] = {
    ("POST", "/api/v1/auth/login"): (5, 60),
    ("POST", "/api/v1/auth/refresh"): (20, 60),
    ("POST", "/api/v1/user"): (3, 60 * 60),
}
ATTENDANCE_PATH = r"/api/v1/semanas/\d+/atividades/registrar/\d{4}"
ATTENDANCE_LIMIT: RateLimit = (10, 60)


class RateLimitMiddleware:
    # ponytail: process-local limits; use Redis when running multiple workers/instances.
    _instances: ClassVar[list[RateLimitMiddleware]] = []

    def __init__(self, app: Callable):
        self.app = app
        self.requests: defaultdict[tuple[str, str, str], list[float]] = defaultdict(
            list
        )
        RateLimitMiddleware._instances.append(self)

    @classmethod
    def reset_all(cls) -> None:
        for instance in cls._instances:
            instance.requests.clear()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = request.url.path.rstrip("/") or "/"
        limit = LIMITS.get((request.method, path))
        bucket = path
        if request.method == "POST" and fullmatch(ATTENDANCE_PATH, path):
            limit = ATTENDANCE_LIMIT
            bucket = "/api/v1/semanas/{semana_id}/atividades/registrar"
        if limit is None:
            await self.app(scope, receive, send)
            return

        max_requests, window_seconds = limit
        now = time.monotonic()
        key = (
            request.client.host if request.client else "unknown",
            request.method,
            bucket,
        )
        timestamps = self.requests[key]
        timestamps[:] = [
            timestamp for timestamp in timestamps if now - timestamp < window_seconds
        ]

        if len(timestamps) >= max_requests:
            retry_after = max(1, int(window_seconds - (now - timestamps[0])))
            response = JSONResponse(
                {"detail": "Too many requests. Try again later."},
                status_code=429,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )
            await response(scope, receive, send)
            return

        timestamps.append(now)
        await self.app(scope, receive, send)
