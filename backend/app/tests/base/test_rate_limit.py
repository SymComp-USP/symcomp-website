import asyncio

from app.core.rate_limit import RateLimitMiddleware


def test_rate_limit_blocks_after_limit():
    calls = 0

    async def app(scope, receive, send):
        nonlocal calls
        calls += 1

    limiter = RateLimitMiddleware(app)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/auth/login",
        "raw_path": b"/api/v1/auth/login",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "server": ("test", 80),
        "scheme": "http",
        "http_version": "1.1",
    }

    sent: list[dict] = []

    async def send(message):
        sent.append(message)

    async def run():
        for _ in range(5):
            await limiter(scope, None, send)
        await limiter(scope, None, send)

    asyncio.run(run())

    assert calls == 5
    assert next(message for message in sent if "status" in message)["status"] == 429


def test_rate_limit_blocks_attendance_code_guessing_across_codes():
    calls = 0

    async def app(scope, receive, send):
        nonlocal calls
        calls += 1

    limiter = RateLimitMiddleware(app)
    sent: list[dict] = []

    async def send(message):
        sent.append(message)

    async def run():
        for code in range(10):
            scope = {
                "type": "http",
                "method": "POST",
                "path": f"/api/v1/semanas/1/atividades/registrar/{code:04}",
                "raw_path": b"",
                "query_string": b"",
                "headers": [],
                "client": ("127.0.0.1", 1234),
                "server": ("test", 80),
                "scheme": "http",
                "http_version": "1.1",
            }
            await limiter(scope, None, send)
        await limiter(scope, None, send)

    asyncio.run(run())

    assert calls == 10
    assert next(message for message in sent if "status" in message)["status"] == 429
