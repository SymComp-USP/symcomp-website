from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Security, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import app.challenges.services.image as cover_image_service
from app.auth.dependencies import get_current_admin_user
from app.auth.scopes import Scope
from app.challenges import schemas as challenge_schemas
from app.challenges.models.challenge import ChallengeScoringType
from app.challenges.services import challenge as challenge_service
from app.challenges.services import challenge_participant as participant_service
from app.challenges.services import input as input_service
from app.challenges.services import question as question_service
from app.core.database import get_session
from app.core.exceptions.app_errors import BadRequestError, NotFoundError
from app.core.pagination import Page, PaginationParams
from app.semana import services as semana_service
from app.users.models import User

router = APIRouter(tags=["admin", "challenges"])

AdminUser = Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])]


# ---------- Challenge ----------


@router.get("", response_model=Page[challenge_schemas.AdminChallengeResponse])
@router.get(
    "/",
    response_model=Page[challenge_schemas.AdminChallengeResponse],
    include_in_schema=False,
)
async def list_challenges_admin(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: AdminUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await challenge_service.list_admin_challenges_paginated(
        session, PaginationParams(limit=limit, offset=offset)
    )


@router.post(
    "", response_model=challenge_schemas.AdminChallengeResponse, status_code=201
)
@router.post(
    "/",
    response_model=challenge_schemas.AdminChallengeResponse,
    include_in_schema=False,
    status_code=201,
)
async def create_challenge_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: challenge_schemas.ChallengeCreate,
    current_user: AdminUser,
):
    """Cria um challenge com título, tipo e (no caso de challenges do tipo quiz) as perguntas dadas"""

    if (
        data.semana_id is not None
        and await semana_service.get_semana(session, data.semana_id) is None
    ):
        raise NotFoundError("Semana not found.")

    challenge = await challenge_service.create_challenge(
        session,
        title=data.title,
        description=data.description,
        scoring_type=data.scoring_type,
        finishes_at=data.finishes_at,
        semana_id=data.semana_id,
        points_value=data.points_value,
        resource_urls=data.resource_urls,
    )

    if data.questions:
        await question_service.replace_challenge_questions(
            session, challenge, data.questions
        )
    elif data.scoring_type == ChallengeScoringType.INPUT:
        await input_service.create_input(
            session,
            challenge,
            prompt=data.prompt or "",
            input_answer=data.input_answer,
        )

    return await get_challenge_admin(session, challenge.id, current_user)


@router.patch(
    "/{challenge_id}", response_model=challenge_schemas.AdminChallengeResponse
)
async def update_challenge_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    data: challenge_schemas.ChallengeUpdate,
    current_user: AdminUser,
):
    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found.")

    scoring_type = data.scoring_type or challenge.scoring_type
    if data.questions and scoring_type != ChallengeScoringType.QUIZ:
        raise BadRequestError("Only quiz challenges can have questions.")
    input_data = await input_service.get_input_by_challenge_id(session, challenge.id)
    if scoring_type == ChallengeScoringType.INPUT:
        if input_data is None and (data.prompt is None or not data.input_answer):
            raise BadRequestError("Input challenges require a prompt and an answer.")
        if data.input_answer == "":
            raise BadRequestError("Input challenges require an expected answer.")
    if (
        data.semana_id is not None
        and await semana_service.get_semana(session, data.semana_id) is None
    ):
        raise NotFoundError("Semana not found.")

    await challenge_service.update_challenge(
        session,
        challenge,
        title=data.title,
        description=data.description,
        scoring_type=data.scoring_type,
        finishes_at=data.finishes_at,
        semana_id=data.semana_id,
        points_value=data.points_value,
        resource_urls=data.resource_urls,
    )

    if scoring_type == ChallengeScoringType.QUIZ:
        if input_data is not None:
            await input_service.delete_input(session, input_data)
        if data.questions is not None:
            await question_service.replace_challenge_questions(
                session, challenge, data.questions
            )
    elif scoring_type == ChallengeScoringType.INPUT:
        await question_service.replace_challenge_questions(session, challenge, [])
        if input_data is None:
            await input_service.create_input(
                session,
                challenge,
                prompt=data.prompt or "",
                input_answer=data.input_answer,
            )
        else:
            await input_service.update_input(
                session,
                input_data,
                prompt=data.prompt,
                input_answer=data.input_answer,
            )
    else:
        if input_data is not None:
            await input_service.delete_input(session, input_data)
        await question_service.replace_challenge_questions(session, challenge, [])

    return await get_challenge_admin(session, challenge.id, current_user)


@router.delete("/{challenge_id}", status_code=204)
async def delete_challenge_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    current_user: AdminUser,
):
    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found.")

    await challenge_service.delete_challenge(session, challenge)


@router.get(
    "/participants",
    response_model=Page[challenge_schemas.AdminChallengeParticipantResponse],
)
async def list_challenge_participants_admin(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: AdminUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return await participant_service.list_admin_challenge_participants_paginated(
        session, PaginationParams(limit=limit, offset=offset)
    )


@router.get("/{challenge_id}", response_model=challenge_schemas.AdminChallengeResponse)
async def get_challenge_admin(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    current_user: AdminUser,
):
    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found.")

    return challenge


@router.patch(
    "/{challenge_id}/participants/{participant_id}/score",
    response_model=challenge_schemas.ParticipantScoreResponse,
)
async def adjust_participant_score(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    participant_id: UUID,
    data: challenge_schemas.ParticipantScoreAdjustment,
    current_user: AdminUser,
):
    participant = await participant_service.add_challenge_participant_score(
        session, challenge_id, participant_id, data.amount
    )
    if participant is None:
        raise NotFoundError("Challenge participant not found.")

    if participant.semana_participant is not None:
        await semana_service.add_points(
            session,
            participant.semana_participant,
            data.amount,
            source_type="manual_adjustment",
            reason="Admin score adjustment",
        )

    response = challenge_schemas.ParticipantScoreResponse(
        id=participant.id,
        challenge_id=participant.challenge_id,
        score=participant.score,
    )
    await session.commit()
    return response


# ---------- Challenge Cover Image -----------


@router.put(
    "/{challenge_id}/image", response_model=challenge_schemas.ChallengePublicResponse
)
async def upload_challenge_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    file: Annotated[UploadFile, File()],
    current_user: AdminUser,
):
    """Substitui (ou cria) a imagem do challenge.

    Ordem: grava arquivo novo → commita banco → apaga arquivo antigo.
    Se o flush falhar, apaga o novo para não deixar órfão.
    """
    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found.")

    new_path = await cover_image_service.save_challenge_image(file)
    old_path = challenge.image_path
    challenge.image_path = new_path

    try:
        await session.flush()
        await session.commit()
    except Exception:
        cover_image_service.delete_challenge_image(new_path)
        await session.rollback()
        raise

    # Só depois do banco estar consistente apagamos o antigo
    cover_image_service.delete_challenge_image(old_path)

    return challenge_schemas.ChallengePublicResponse.model_validate(challenge)


@router.delete("/{challenge_id}/image", status_code=204)
async def delete_challenge_image_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    current_user: AdminUser,
):
    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found.")

    old_path = challenge.image_path
    challenge.image_path = None
    try:
        await session.flush()
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    cover_image_service.delete_challenge_image(old_path)
