"""Testes dos endpoints de admin."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.models.input import Input
from app.challenges.models.question import Question


async def test_non_admin_is_forbidden(client: AsyncClient, as_user, user):
    c = as_user(user)
    r = await c.post("/api/v1/admin/challenge/", json={"title": "X"})
    assert r.status_code == 403


async def test_admin_can_create_challenge(client: AsyncClient, as_user, admin):
    c = as_user(admin)
    r = await c.post(
        "/api/v1/admin/challenge/",
        json={"title": "Novo", "scoring_type": "quiz"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["title"] == "Novo"
    assert body["scoring_type"] == "quiz"
    default_deadline = datetime.fromisoformat(body["finishes_at"])
    assert default_deadline.tzinfo is not None
    assert timedelta(hours=23, minutes=59) <= default_deadline - datetime.now(UTC)
    assert default_deadline - datetime.now(UTC) <= timedelta(days=1, minutes=1)
    assert body["questions"] == []


async def test_admin_can_create_challenge_with_questions(
    client: AsyncClient, as_user, admin
):
    c = as_user(admin)
    r = await c.post(
        "/api/v1/admin/challenge/",
        json={
            "title": "Quiz com perguntas",
            "points_value": 60,
            "questions": [
                {"prompt": "2+2?", "answer": "4"},
                {"prompt": "3+3?", "answer": "6"},
            ],
        },
    )

    assert r.status_code == 201, r.text
    created_questions = r.json()["questions"]
    assert len(created_questions) == 2
    assert created_questions[0]["prompt"] == "2+2?"
    assert r.json()["points_value"] == 60


async def test_admin_can_create_input_challenge(
    client: AsyncClient, as_user, admin, db_session: AsyncSession
):
    c = as_user(admin)
    r = await c.post(
        "/api/v1/admin/challenge/",
        json={
            "title": "Resposta livre",
            "scoring_type": "input",
            "prompt": "Qual é a resposta?",
            "points_value": 20,
            "input_answer": "42",
        },
    )

    assert r.status_code == 201, r.text
    body = r.json()
    assert body["prompt"] == "Qual é a resposta?"
    assert body["points_value"] == 20
    assert body["input_answer"] == "42"
    input_data = await db_session.scalar(
        select(Input).where(Input.challenge_id == body["id"])
    )
    assert input_data is not None


async def test_admin_rejects_input_challenge_without_answer(
    client: AsyncClient, as_user, admin
):
    c = as_user(admin)
    r = await c.post(
        "/api/v1/admin/challenge/",
        json={"title": "Resposta livre", "scoring_type": "input", "prompt": "Q?"},
    )

    assert r.status_code == 422


async def test_admin_can_update_input_challenge(client: AsyncClient, as_user, admin):
    c = as_user(admin)
    created = await c.post(
        "/api/v1/admin/challenge/",
        json={
            "title": "Resposta livre",
            "scoring_type": "input",
            "prompt": "Q?",
            "input_answer": "42",
        },
    )
    challenge_id = created.json()["id"]

    r = await c.patch(
        f"/api/v1/admin/challenge/{challenge_id}",
        json={"prompt": "Nova pergunta", "points_value": 35},
    )

    assert r.status_code == 200, r.text
    assert r.json()["prompt"] == "Nova pergunta"
    assert r.json()["points_value"] == 35
    assert r.json()["input_answer"] == "42"


async def test_admin_can_set_challenge_deadline(client: AsyncClient, as_user, admin):
    c = as_user(admin)
    deadline = datetime(2099, 1, 1, tzinfo=UTC)
    r = await c.post(
        "/api/v1/admin/challenge/",
        json={"title": "Prazo definido", "finishes_at": deadline.isoformat()},
    )
    assert r.status_code == 201, r.text
    assert datetime.fromisoformat(r.json()["finishes_at"]) == deadline


async def test_admin_rejects_challenge_deadline_without_timezone(
    client: AsyncClient, as_user, admin
):
    c = as_user(admin)
    r = await c.post(
        "/api/v1/admin/challenge/",
        json={"title": "Prazo sem fuso", "finishes_at": "2099-01-01T00:00:00"},
    )
    assert r.status_code == 422


async def test_admin_patch_without_questions_preserves_existing_questions(
    client: AsyncClient, as_user, admin, challenge, questions
):
    c = as_user(admin)
    original_ids = {str(question.id) for question in questions}

    r = await c.patch(
        f"/api/v1/admin/challenge/{challenge.id}", json={"title": "Renamed"}
    )

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["title"] == "Renamed"
    assert {question["id"] for question in body["questions"]} == original_ids


async def test_admin_can_update_challenge_deadline(
    client: AsyncClient, as_user, admin, challenge
):
    c = as_user(admin)
    deadline = datetime(2099, 6, 1, 12, 30, tzinfo=UTC)

    r = await c.patch(
        f"/api/v1/admin/challenge/{challenge.id}",
        json={"finishes_at": deadline.isoformat()},
    )

    assert r.status_code == 200, r.text
    assert datetime.fromisoformat(r.json()["finishes_at"]) == deadline


async def test_admin_rejects_patch_deadline_without_timezone(
    client: AsyncClient, as_user, admin, challenge
):
    c = as_user(admin)
    r = await c.patch(
        f"/api/v1/admin/challenge/{challenge.id}",
        json={"finishes_at": "2099-06-01T12:30:00"},
    )
    assert r.status_code == 422


async def test_admin_patch_replaces_questions_and_hard_deletes_old_ones(
    client: AsyncClient,
    as_user,
    admin,
    challenge,
    questions,
    db_session: AsyncSession,
):
    c = as_user(admin)
    old_ids = {question.id for question in questions}

    r = await c.patch(
        f"/api/v1/admin/challenge/{challenge.id}",
        json={"questions": [{"prompt": "New prompt", "answer": "New answer"}]},
    )

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["title"] == challenge.title
    assert len(body["questions"]) == 1
    assert body["questions"][0]["prompt"] == "New prompt"
    assert body["questions"][0]["answer"] == "New answer"
    remaining_old_ids = set(
        (
            await db_session.scalars(
                select(Question.id).where(Question.id.in_(old_ids))
            )
        ).all()
    )
    assert remaining_old_ids == set()


async def test_admin_patch_with_empty_questions_clears_existing_questions(
    client: AsyncClient, as_user, admin, challenge, questions
):
    c = as_user(admin)

    r = await c.patch(f"/api/v1/admin/challenge/{challenge.id}", json={"questions": []})

    assert r.status_code == 200, r.text
    assert r.json()["questions"] == []


async def test_admin_get_challenge_with_questions(
    client: AsyncClient, as_user, admin, challenge, questions
):
    c = as_user(admin)
    r = await c.get(f"/api/v1/admin/challenge/{challenge.id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["questions"]) == len(questions)


async def test_admin_delete_challenge(client: AsyncClient, as_user, admin, challenge):
    c = as_user(admin)
    r = await c.delete(f"/api/v1/admin/challenge/{challenge.id}")
    assert r.status_code == 204

    # Desaparece do público
    r = await c.get(f"/challenges/{challenge.id}")
    assert r.status_code == 404


async def test_admin_can_add_and_subtract_participant_score(
    client: AsyncClient,
    as_user,
    admin,
    user,
    challenge,
    db_session: AsyncSession,
):
    participant = ChallengeParticipant(
        user_id=user.id, challenge_id=challenge.id, score=40
    )
    db_session.add(participant)
    await db_session.flush()
    c = as_user(admin)

    add_response = await c.patch(
        f"/api/v1/admin/challenge/{challenge.id}/participants/{participant.id}/score",
        json={"amount": 15},
    )
    assert add_response.status_code == 200, add_response.text
    assert add_response.json() == {
        "id": str(participant.id),
        "challenge_id": str(challenge.id),
        "score": 55,
    }

    subtract_response = await c.patch(
        f"/api/v1/admin/challenge/{challenge.id}/participants/{participant.id}/score",
        json={"amount": -70},
    )
    assert subtract_response.status_code == 200, subtract_response.text
    assert subtract_response.json()["score"] == -15


async def test_admin_score_adjustment_requires_matching_challenge(
    client: AsyncClient, as_user, admin, user, challenge, manual_challenge, db_session
):
    participant = ChallengeParticipant(user_id=user.id, challenge_id=challenge.id)
    db_session.add(participant)
    await db_session.flush()
    c = as_user(admin)

    response = await c.patch(
        f"/api/v1/admin/challenge/{manual_challenge.id}/participants/{participant.id}/score",
        json={"amount": 10},
    )

    assert response.status_code == 404
