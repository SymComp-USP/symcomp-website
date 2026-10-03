"""Listagem paginada e ranking."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.semana.models import SemanaParticipant


async def test_list_challenges_paginated(
    client: AsyncClient, as_user, user, db_session: AsyncSession
):
    for i in range(5):
        db_session.add(Challenge(title=f"C{i}", scoring_type=ChallengeScoringType.QUIZ))
    future_challenge = Challenge(
        title="Future challenge",
        scoring_type=ChallengeScoringType.QUIZ,
        starts_at=datetime.now(UTC) + timedelta(days=1),
    )
    db_session.add(future_challenge)
    await db_session.flush()

    c = as_user(user)

    anonymous_list = await client.get(
        "/api/v1/challenge", params={"limit": 100, "offset": 0}
    )
    assert anonymous_list.status_code == 200
    assert anonymous_list.json()["total"] == 5
    assert all(
        item["id"] != str(future_challenge.id)
        for item in anonymous_list.json()["items"]
    )

    r = await c.get("api/v1/challenge", params={"limit": 2, "offset": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert len(body["items"]) == 2

    r = await c.get("api/v1/challenge/", params={"limit": 2, "offset": 4})
    assert len(r.json()["items"]) == 1


async def test_future_challenge_is_hidden_from_public_detail_and_ranking(
    client: AsyncClient, as_user, user, challenge, db_session: AsyncSession
):
    challenge.starts_at = datetime.now(UTC) + timedelta(days=1)
    await db_session.flush()

    c = as_user(user)
    detail = await c.get(f"/api/v1/challenge/{challenge.id}")
    ranking = await c.get(f"/api/v1/challenge/{challenge.id}/ranking")

    assert detail.status_code == 404
    assert ranking.status_code == 404


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
    semana,
):
    from app.users.models import User

    ranking_nickname = "AdaLovelace4821"

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
            semana_participant = SemanaParticipant(
                user_id=u.id,
                semana_id=semana.id,
                nickname=ranking_nickname,
            )
            db_session.add(semana_participant)
            await db_session.flush()
        else:
            semana_participant = None
        db_session.add(
            ChallengeParticipant(
                user_id=u.id,
                challenge_id=challenge.id,
                score=i * 10,
                semana_participant_id=(
                    semana_participant.id if semana_participant is not None else None
                ),
            )
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
    assert ranking[0]["nickname"] == ranking_nickname
