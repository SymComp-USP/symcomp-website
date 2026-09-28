"""Listagem paginada e ranking."""

from __future__ import annotations

import uuid

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.challenges.models.challenge_participant import ChallengeParticipant


async def test_list_challenges_paginated(
    client: AsyncClient, as_user, user, db_session: AsyncSession
):
    for i in range(5):
        db_session.add(Challenge(title=f"C{i}", scoring_type=ChallengeScoringType.QUIZ))
    await db_session.flush()

    c = as_user(user)

    r = await c.get("api/v1/challenge/", params={"limit": 2, "offset": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert len(body["items"]) == 2

    r = await c.get("api/v1/challenge/", params={"limit": 2, "offset": 4})
    assert len(r.json()["items"]) == 1


async def test_list_rejects_bad_pagination(client: AsyncClient, as_user, user):
    c = as_user(user)
    r = await c.get("api/v1/challenge/", params={"limit": 0})
    assert r.status_code == 422

    r = await c.get("api/v1/challenge/", params={"limit": 10000})
    assert r.status_code == 422


async def test_ranking_orders_by_score_desc(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    db_session: AsyncSession,
    username_catalog,
):
    from app.users.models import User

    # 15 participantes com scores variados
    for i in range(15):
        u = User(
            id=uuid.uuid4(),
            email=f"u{i}@t.local",
            name=f"U{i}",
            password_hash="x",
            is_verified=True,
        )
        db_session.add(u)
        await db_session.flush()
        if i == 14:
            u.username_id = username_catalog[0].id
        db_session.add(
            ChallengeParticipant(user_id=u.id, challenge_id=challenge.id, score=i * 10)
        )
    await db_session.flush()

    c = as_user(user)
    r = await c.get(f"api/v1/challenge/{challenge.id}/ranking")
    assert r.status_code == 200
    ranking = r.json()
    assert len(ranking) == 10  # top 10
    scores = [p["score"] for p in ranking]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 140
    assert ranking[0]["nickname"] == username_catalog[0].nickname
