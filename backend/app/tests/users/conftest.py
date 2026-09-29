"""Fixtures para os testes do módulo de usuários."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest
from httpx2 import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_admin_user, get_current_user
from app.users.models import User


@pytest.fixture
async def admin_user(db_session: AsyncSession, user_factory) -> User:
    user = await user_factory(email="admin-fixture@example.com", name="Admin")
    user.is_admin = True
    user.is_verified = True
    await db_session.flush()
    return user


@pytest.fixture
async def regular_user(user_factory) -> User:
    return await user_factory(email="regular-fixture@example.com", name="Regular")


@pytest.fixture
def as_user(db_client: AsyncClient) -> Iterator[Callable[[User], AsyncClient]]:
    """Faz override da autenticação. `as_user(user)` retorna o client autenticado
    como esse usuário (o check de `is_admin` continua valendo)."""

    app = db_client._transport.app

    def _switch(user: User) -> AsyncClient:
        app.dependency_overrides[get_current_user] = lambda: user
        return db_client

    yield _switch

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_admin_user, None)
