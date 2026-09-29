"""Ciclo completo: join → answer → submit → ranking."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


async def test_full_quiz_lifecycle(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    questions,
    username_catalog,
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

    # 5. Submit
    r = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["score"] == 150  # 100 + 50
    assert body["submitted_at"] is not None

    # 6. Submit de novo → idempotente
    r2 = await c.post(f"api/v1/challenge/{challenge.id}/submit")
    assert r2.status_code == 200
    assert r2.json() == body

    # 7. Ranking
    r = await c.get(f"api/v1/challenge/{challenge.id}/ranking")
    assert r.status_code == 200
    ranking = r.json()
    assert len(ranking) == 1
    assert ranking[0]["score"] == 150


async def test_answering_without_joining_returns_400(
    client: AsyncClient, as_user, user, challenge, questions
):
    c = as_user(user)
    r = await c.post(
        f"api/v1/challenge/{challenge.id}/answer",
        json={"question_id": str(questions[0].id), "answer": "4"},
    )
    assert r.status_code == 400


async def test_username_is_reused_across_challenge_joins(
    client: AsyncClient,
    as_user,
    user,
    challenge,
    manual_challenge,
    username_catalog,
):
    c = as_user(user)

    first_join = await c.post(f"api/v1/challenge/{challenge.id}/join")
    second_join = await c.post(f"api/v1/challenge/{manual_challenge.id}/join")

    assert first_join.status_code == 200, first_join.text
    assert second_join.status_code == 200, second_join.text
    assert first_join.json()["nickname"] in {
        username.nickname for username in username_catalog
    }
    assert second_join.json()["nickname"] == first_join.json()["nickname"]


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
    username_catalog,
    db_session,
):
    from app.challenges.models.question import Question

    q = Question(
        prompt="?", answer="?", points_value=10, challenge_id=manual_challenge.id
    )
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
    client: AsyncClient, as_user, user, challenge, questions, username_catalog
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
    username_catalog,
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
    username_catalog,
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
    username_catalog,
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
