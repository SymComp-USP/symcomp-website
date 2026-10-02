"""Ciclo completo: join → answer → submit → ranking."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import func, select

from app.challenges.models.challenge import ChallengeScoringType
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.models.input import Input
from app.semana.models import PointEvent, SemanaEvent, SemanaParticipant


async def test_input_challenge_scores_using_challenge_points(
    client: AsyncClient, as_user, user, challenge, db_session
):
    challenge.scoring_type = ChallengeScoringType.INPUT
    challenge.points_value = 40
    challenge.input = Input(prompt="Answer?", input_answer="correct")
    await db_session.flush()

    c = as_user(user)
    joined = await c.post(f"api/v1/challenge/{challenge.id}/join")
    assert joined.status_code == 200, joined.text

    response = await c.post(
        f"api/v1/challenge/{challenge.id}/input", json={"answer": "incorrect"}
    )

    assert response.status_code == 200, response.text
    assert response.json() == {"submitted_at": None, "score": 0}

    challenge_state = await c.get(f"api/v1/challenge/{challenge.id}")
    assert challenge_state.status_code == 200, challenge_state.text
    assert challenge_state.json()["submitted_at"] is None
    assert "input_answer" not in challenge_state.json()

    participant = await db_session.scalar(
        select(ChallengeParticipant).where(
            ChallengeParticipant.user_id == user.id,
            ChallengeParticipant.challenge_id == challenge.id,
        )
    )
    assert participant is not None
    assert await db_session.scalar(
        select(func.count(PointEvent.id)).where(
            PointEvent.source_type == "challenge",
            PointEvent.source_id == participant.id,
        )
    ) == 0

    correct_response = await c.post(
        f"api/v1/challenge/{challenge.id}/input", json={"answer": "correct"}
    )
    assert correct_response.status_code == 200, correct_response.text
    assert correct_response.json()["score"] == 40
    assert correct_response.json()["submitted_at"] is not None

    challenge_state = await c.get(f"api/v1/challenge/{challenge.id}")
    assert challenge_state.json()["submitted_at"] == correct_response.json()[
        "submitted_at"
    ]
    assert challenge_state.json()["score"] == 40

    repeated_response = await c.post(
        f"api/v1/challenge/{challenge.id}/input", json={"answer": "incorrect"}
    )
    assert repeated_response.status_code == 200, repeated_response.text
    assert repeated_response.json() == correct_response.json()
    assert await db_session.scalar(
        select(func.count(PointEvent.id)).where(
            PointEvent.source_type == "challenge",
            PointEvent.source_id == participant.id,
        )
    ) == 1


async def test_input_submission_is_rejected_after_challenge_expires(
    client: AsyncClient, as_user, user, challenge, db_session
):
    challenge.scoring_type = ChallengeScoringType.INPUT
    challenge.input = Input(prompt="Answer?", input_answer="correct")
    await db_session.flush()

    c = as_user(user)
    joined = await c.post(f"api/v1/challenge/{challenge.id}/join")
    assert joined.status_code == 200, joined.text

    challenge.finishes_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    response = await c.post(
        f"api/v1/challenge/{challenge.id}/input", json={"answer": "incorrect"}
    )

    assert response.status_code == 400


async def test_full_quiz_lifecycle(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    questions,
    db_session,
):
    c = as_user(user)

    # 1. Join
    r = await c.post(f"api/v1/challenge/{challenge.id}/join")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["challenge_id"] == str(challenge.id)
    assert body["score"] == 0
    assert body["submitted_at"] is None

    # 2. Join de novo → 400
    r = await c.post(f"api/v1/challenge/{challenge.id}/join")
    assert r.status_code == 400

    # 3. Salvar respostas
    r = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[0].id), "answer": "4"},
    )
    assert r.status_code == 204

    r = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[1].id), "answer": "9"},
    )
    assert r.status_code == 204

    r = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[2].id), "answer": "Rio"},
    )
    assert r.status_code == 204

    # 4. GET /challenge → deve mostrar current_answer
    r = await c.get(f"api/v1/challenge/{challenge.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["is_participant"] is True
    assert data["submitted_at"] is None
    answers_by_qid = {q["id"]: q["current_answer"] for q in data["questions"]}
    assert answers_by_qid[str(questions[0].id)] == "4"
    assert answers_by_qid[str(questions[1].id)] == "9"
    assert answers_by_qid[str(questions[2].id)] == "Rio"

    # 5. Submit with one incorrect answer; retry remains available.
    r = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["score"] == 150
    assert body["submitted_at"] is None

    participant = await db_session.scalar(
        select(ChallengeParticipant).where(
            ChallengeParticipant.user_id == user.id,
            ChallengeParticipant.challenge_id == challenge.id,
        )
    )
    assert participant is not None
    assert await db_session.scalar(
        select(func.count(PointEvent.id)).where(
            PointEvent.source_type == "challenge",
            PointEvent.source_id == participant.id,
        )
    ) == 0

    retry = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[2].id), "answer": "Brasília"},
    )
    assert retry.status_code == 204

    completed = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert completed.status_code == 200, completed.text
    body = completed.json()
    assert body["score"] == 225
    assert body["submitted_at"] is not None

    completed_details = await c.get(f"api/v1/challenge/{challenge.id}")
    assert completed_details.json()["submitted_at"] == body["submitted_at"]
    assert completed_details.json()["score"] == 225

    blocked_edit = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[2].id), "answer": "Rio"},
    )
    assert blocked_edit.status_code == 400

    # 6. Submit de novo → idempotente
    r2 = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r2.status_code == 200
    assert r2.json() == body
    assert await db_session.scalar(
        select(func.count(PointEvent.id)).where(
            PointEvent.source_type == "challenge",
            PointEvent.source_id == participant.id,
        )
    ) == 1

    # 7. Ranking
    r = await c.get(f"api/v1/challenge/{challenge.id}/ranking")
    assert r.status_code == 200
    ranking = r.json()
    assert len(ranking) == 1
    assert ranking[0]["score"] == 225


async def test_quiz_submission_is_rejected_after_challenge_expires(
    client: AsyncClient, as_user, user, challenge, db_session
):
    c = as_user(user)
    joined = await c.post(f"api/v1/challenge/{challenge.id}/join")
    assert joined.status_code == 200, joined.text

    challenge.finishes_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    response = await c.post(f"api/v1/challenge/{challenge.id}/submit")

    assert response.status_code == 400


async def test_answering_without_joining_returns_400(
    client: AsyncClient, as_user, user, challenge, questions
):
    c = as_user(user)
    r = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[0].id), "answer": "4"},
    )
    assert r.status_code == 400


async def test_nickname_is_reused_across_challenge_joins(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    manual_challenge,
):
    c = as_user(user)

    first_join = await c.post(f"api/v1/challenge/{challenge.id}/join")
    second_join = await c.post(f"api/v1/challenge/{manual_challenge.id}/join")

    assert first_join.status_code == 200, first_join.text
    assert second_join.status_code == 200, second_join.text
    assert len(first_join.json()["nickname"]) > 0
    assert re.fullmatch(r"[A-Za-z]+\d{4}", first_join.json()["nickname"])
    assert second_join.json()["nickname"] == first_join.json()["nickname"]


async def test_profile_returns_the_nickname_for_each_week(
    client: AsyncClient, as_user, user, challenge, db_session
):
    c = as_user(user)
    joined = await c.post(f"api/v1/challenge/{challenge.id}/join")
    assert joined.status_code == 200, joined.text

    other_week = SemanaEvent(nome="Outra Semana", ano=2025)
    db_session.add(other_week)
    await db_session.flush()
    db_session.add(
        SemanaParticipant(
            semana_id=other_week.id,
            user_id=user.id,
            nickname="OutraPessoa2025",
        )
    )
    await db_session.flush()

    response = await c.get("/api/v1/semanas/participacao")

    assert response.status_code == 200, response.text
    weeks = {week["semana_id"]: week for week in response.json()["semanas"]}
    assert weeks[challenge.semana_id]["nickname"] == joined.json()["nickname"]
    assert weeks[other_week.id]["nickname"] == "OutraPessoa2025"


async def test_submitting_without_joining_returns_400(
    client: AsyncClient, as_user, user, challenge
):
    c = as_user(user)
    r = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r.status_code == 400


async def test_submitting_question_from_other_challenge_returns_404(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    manual_challenge,
    db_session,
):
    from app.challenges.models.question import Question

    q = Question(prompt="?", answer="?", challenge_id=manual_challenge.id)
    db_session.add(q)
    await db_session.flush()

    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")

    r = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(q.id), "answer": "x"},
    )
    assert r.status_code == 404


async def test_bulk_save_answers(
    client: AsyncClient, as_user, user, challenge, questions
):
    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")

    payload = [
        {"question_id": str(questions[0].id), "answer": "4"},
        {"question_id": str(questions[1].id), "answer": "9"},
    ]
    r = await c.post(f"api/v1/challenge/{challenge.id}/answer/all", json=payload)
    assert r.status_code == 204

    r = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r.json()["score"] == 150


async def test_expired_challenge_rejects_single_and_bulk_answers(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    questions,
    db_session,
):
    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")
    challenge.finishes_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    single = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[0].id), "answer": "4"},
    )
    bulk = await c.post(
        f"api/v1/challenge/{challenge.id}/answer/all",
        json=[{"question_id": str(questions[1].id), "answer": "9"}],
    )

    for response in (single, bulk):
        assert response.status_code == 409
        body = response.json()
        assert body["type"] == "challenge_closed"
        assert body["detail"] == (
            "This challenge has ended and no longer accepts answers or submissions."
        )


async def test_expired_challenge_rejects_new_submission(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    db_session,
):
    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")
    challenge.finishes_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()

    response = await c.post(f"api/v1/challenge/{challenge.id}/submit")

    assert response.status_code == 409
    assert response.json()["type"] == "challenge_closed"
    assert response.json()["detail"] == (
        "This challenge has ended and no longer accepts answers or submissions."
    )


async def test_existing_submission_remains_idempotent_after_deadline(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    db_session,
):
    c = as_user(user)
    await c.post(f"api/v1/challenge/{challenge.id}/join")
    first_response = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert first_response.status_code == 200

    challenge.finishes_at = datetime.now(UTC) - timedelta(seconds=1)
    await db_session.flush()
    retry_response = await c.post(f"api/v1/challenge/{challenge.id}/submit")

    assert retry_response.status_code == 200
    assert retry_response.json() == first_response.json()


async def test_get_challenge_not_found(client: AsyncClient, as_user, user):
    import uuid

    c = as_user(user)
    r = await c.get(f"api/v1/challenge/{uuid.uuid4()}")
    assert r.status_code == 404
