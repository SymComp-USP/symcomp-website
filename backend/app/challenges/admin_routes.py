from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Security, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

import app.challenges.services.image as cover_image_service
from app.auth.dependencies import get_current_admin_user
from app.auth.scopes import Scope
from app.challenges import schemas as challenge_schemas
from app.challenges.models.challenge import ChallengeScoringType
from app.challenges.services import challenge as challenge_service
from app.challenges.services import challenge_participant as participant_service
from app.challenges.services import question as question_service
from app.core.database import get_session
from app.core.exceptions.app_errors import BadRequestError, NotFoundError
from app.users.models import User

router = APIRouter(tags=["admin", "challenges"])

AdminUser = Annotated[User, Security(get_current_admin_user, scopes=[Scope.ADMIN])]


# ---------- Challenge ----------


@router.post(
    "/", response_model=challenge_schemas.AdminChallengeResponse, status_code=201
)
async def create_challenge_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: challenge_schemas.ChallengeCreate,
    current_user: AdminUser,
):
    """Cria um challenge com título, tipo e (no caso de challenges do tipo quiz) as perguntas dadas"""

    if len(data.questions) != 0 and data.scoring_type == ChallengeScoringType.MANUAL:
        raise BadRequestError("Manual challenges cannot have questions.")

    challenge = await challenge_service.create_challenge(
        session,
        title=data.title,
        scoring_type=data.scoring_type,
        finishes_at=data.finishes_at,
    )

    if data.questions:
        await question_service.replace_challenge_questions(
            session, challenge, data.questions
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

    if data.questions and challenge.scoring_type == ChallengeScoringType.MANUAL:
        raise BadRequestError("Manual challenges cannot have questions.")

    await challenge_service.update_challenge(
        session,
        challenge,
        title=data.title,
        finishes_at=data.finishes_at,
    )
    if data.questions is not None:
        await question_service.replace_challenge_questions(
            session, challenge, data.questions
        )

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

    return challenge_schemas.ParticipantScoreResponse(
        id=participant.id,
        challenge_id=participant.challenge_id,
        score=participant.score,
    )


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
    except Exception:
        cover_image_service.delete_challenge_image(new_path)
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
    await session.flush()

    cover_image_service.delete_challenge_image(old_path)
