"""Fixtures para os testes do domínio de challenges."""

from __future__ import annotations

import uuid
from collections.abc import Callable

import pytest
from app.auth.dependencies import get_current_admin_user, get_current_user
from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.challenges.models.question import Question
from app.semana.models import SemanaEvent
from app.users.models import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def _make_user(*, is_admin: bool = False) -> User:
    # Ajuste os nomes dos campos conforme o seu User model.
    return User(
        id=uuid.uuid4(),
        email=f"user-{uuid.uuid4()}@test.local",
        name="Test User",
        password_hash="not-used-in-tests",
        is_verified=True,
        is_admin=is_admin,
    )


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    u = _make_user()
    db_session.add(u)
    await db_session.flush()
    return u


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    u = _make_user()
    db_session.add(u)
    await db_session.flush()
    return u


@pytest.fixture
async def admin(db_session: AsyncSession) -> User:
    u = _make_user(is_admin=True)
    db_session.add(u)
    await db_session.flush()
    return u


# ---------------------------------------------------------------------------
# Auth override
# ---------------------------------------------------------------------------


@pytest.fixture
def as_user(db_client: AsyncClient) -> Callable[[User], AsyncClient]:
    """Override das dependências de auth. Uso: `as_user(user)` retorna o client
    configurado para essa identidade."""

    app = db_client._transport.app

    def _switch(user: User) -> AsyncClient:
        app.dependency_overrides[get_current_user] = lambda: user
        return db_client

    yield _switch

    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_admin_user, None)


# ---------------------------------------------------------------------------
# Domain fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def semana(db_session: AsyncSession) -> SemanaEvent:
    event = SemanaEvent(nome="Semana Teste", ano=2026)
    db_session.add(event)
    await db_session.flush()
    return event


@pytest.fixture
async def challenge(db_session: AsyncSession, semana: SemanaEvent) -> Challenge:
    c = Challenge(
        title="Quiz Teste",
        scoring_type=ChallengeScoringType.QUIZ,
        semana_id=semana.id,
    )
    db_session.add(c)
    await db_session.flush()
    return c


@pytest.fixture
async def manual_challenge(
    db_session: AsyncSession, semana: SemanaEvent
) -> Challenge:
    c = Challenge(
        title="Manual Teste",
        scoring_type=ChallengeScoringType.MANUAL,
        semana_id=semana.id,
    )
    db_session.add(c)
    await db_session.flush()
    return c


@pytest.fixture
async def questions(db_session: AsyncSession, challenge: Challenge) -> list[Question]:
    qs = [
        Question(
            prompt="2+2?",
            answer="4",
            points_value=100,
            challenge_id=challenge.id,
        ),
        Question(
            prompt="3*3?",
            answer="9",
            points_value=50,
            challenge_id=challenge.id,
        ),
        Question(
            prompt="Capital do Brasil?",
            answer="Brasília",
            points_value=75,
            challenge_id=challenge.id,
        ),
    ]
    for q in qs:
        db_session.add(q)
    await db_session.flush()
    return qs
