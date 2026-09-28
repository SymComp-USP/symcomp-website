"""Challenges MANUAL não têm perguntas nem permitem submit."""

from __future__ import annotations

from httpx import AsyncClient


async def test_manual_challenge_cannot_be_submitted(
    client: AsyncClient,
    as_user,
    user,
    manual_challenge,
    username_catalog,
):
    c = as_user(user)
    r = await c.post(f"api/v1/challenge/{manual_challenge.id}/join")
    assert r.status_code == 200

    r = await c.post(f"api/v1/challenge/{manual_challenge.id}/submit")
    assert r.status_code == 400


async def test_manual_challenge_cannot_receive_questions(
    client: AsyncClient, as_user, admin, manual_challenge
):
    c = as_user(admin)
    r = await c.patch(
        f"api/v1/admin/challenge/{manual_challenge.id}",
        json={"questions": [{"prompt": "?", "answer": "!", "points_value": 10}]},
    )
    assert r.status_code == 400
