from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.database import get_session


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [None, "request", "commit"])
async def test_request_transaction(failure):
    session = AsyncMock()
    session.__aenter__.return_value = session
    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(session_factory=MagicMock(return_value=session))
        )
    )
    dependency = get_session(request)
    assert await anext(dependency) is session

    if failure == "request":
        with pytest.raises(ValueError, match="request failed"):
            await dependency.athrow(ValueError("request failed"))
        session.commit.assert_not_awaited()
    elif failure == "commit":
        session.commit.side_effect = ValueError("commit failed")
        with pytest.raises(ValueError, match="commit failed"):
            await anext(dependency)
        session.commit.assert_awaited_once()
    else:
        with pytest.raises(StopAsyncIteration):
            await anext(dependency)
        session.commit.assert_awaited_once()

    if failure:
        session.rollback.assert_awaited_once()
    else:
        session.rollback.assert_not_awaited()
