from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.scopes import Scope
from app.challenges import schemas as challenge_schemas
from app.challenges.models.challenge import ChallengeScoringType
from app.challenges.services import answer as answer_service
from app.challenges.services import challenge as challenge_service
from app.challenges.services import challenge_participant as participant_service
from app.core.database import get_session
from app.core.exceptions.app_errors import BadRequestError, NotFoundError
from app.core.pagination import Page, PaginationParams
from app.semana import services as semana_service
from app.users.models import User

router = APIRouter(tags=["challenges"])


@router.post(
    "/{challenge_id}/join", response_model=challenge_schemas.ParticipantResponse
)
async def join_challenge(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge with given ID not found.")
    if challenge.semana_id is None:
        raise BadRequestError("Challenge must belong to a Semana.")

    current_participant = await participant_service.get_challenge_participant(
        session, current_user.id, challenge_id, for_update=True
    )
    if current_participant is not None:
        raise BadRequestError("You are subscribed to this challenge already.")

    semana = await semana_service.get_semana(session, challenge.semana_id)
    if semana is None:
        raise NotFoundError("Semana not found.")
    semana_participant = await semana_service.get_or_create_participant(
        session, semana, current_user
    )
    semana_participant_id = semana_participant.id

    new_participant = await participant_service.create_challenge_participant(
        session,
        current_user.id,
        challenge_id,
        semana_participant_id=semana_participant_id,
    )
    await session.refresh(new_participant)

    result = await participant_service.get_challenge_participant_by_id(
        session, new_participant.id
    )
    if result is None or result.semana_participant is None:
        raise BadRequestError("Nickname assignment failed.")

    return challenge_schemas.ParticipantResponse(
        id=result.id,
        user_id=result.user_id,
        challenge_id=result.challenge_id,
        name=result.user.name,
        nickname=(
            result.semana_participant.nickname if result.semana_participant else ""
        ),
        score=result.score,
        submitted_at=result.submitted_at,
    )


@router.post("/{challenge_id}/answer", status_code=204)
async def save_answer(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: challenge_schemas.AnswerBody,
    challenge_id: UUID,
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    """Salva uma resposta do usuário (sem submeter) e atualiza seu atributo 'is_correct' de acordo com a resposta esperada da questão."""

    participant = await participant_service.get_challenge_participant(
        session, current_user.id, challenge_id, for_update=False
    )

    if participant is None:
        raise BadRequestError("You are not subscribed to this challenge.")
    if participant.submitted_at is not None:
        raise BadRequestError("Challenge submission is already complete.")

    await answer_service.upsert_answer(
        session, participant.id, data.question_id, data.answer
    )


@router.post(
    "/{challenge_id}/input", response_model=challenge_schemas.SubmissionResponse
)
async def submit_input(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    data: challenge_schemas.InputSubmission,
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    participant = await participant_service.get_challenge_participant(
        session, current_user.id, challenge_id, for_update=True
    )
    if participant is None:
        raise BadRequestError("You are not subscribed to this challenge.")

    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found.")
    if challenge.scoring_type != ChallengeScoringType.INPUT:
        raise BadRequestError("Challenge does not accept input submissions.")
    challenge_service.ensure_challenge_open(challenge.finishes_at)
    if participant.submitted_at is not None:
        return challenge_schemas.SubmissionResponse(
            submitted_at=participant.submitted_at, score=participant.score
        )

    participant.submission = data.answer
    input_data = challenge.input
    is_correct = (
        input_data is not None
        and input_data.input_answer is not None
        and data.answer.strip().lower() == input_data.input_answer.strip().lower()
    )
    participant.score = challenge.points_value if is_correct else 0
    if is_correct:
        participant.submitted_at = datetime.now(UTC)
    await session.flush()
    if is_correct and participant.semana_participant is not None:
        await semana_service.add_points(
            session,
            participant.semana_participant,
            participant.score,
            source_type="challenge",
            source_id=participant.id,
            reason=challenge.title,
        )
    return challenge_schemas.SubmissionResponse(
        submitted_at=participant.submitted_at, score=participant.score
    )


@router.post("/{challenge_id}/answer/all", status_code=204)
async def save_many_answers(
    session: Annotated[AsyncSession, Depends(get_session)],
    data: list[challenge_schemas.AnswerBody],
    challenge_id: UUID,
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    """
    Recebe um payload no formato:
    [
        {question_id: "<id_1>", answer: "resposta da questão com <id_1>",}
        {question_id: "<id_2>", answer: "resposta da questão com <id_2>",}
        ...
    ]

    e salva ou atualiza as respostas do jogador para o challenge informado.
    """

    participant = await participant_service.get_challenge_participant(
        session, current_user.id, challenge_id, for_update=False
    )

    if participant is None:
        raise BadRequestError("You are not subscribed to this challenge.")
    if participant.submitted_at is not None:
        raise BadRequestError("Challenge submission is already complete.")

    for answer_body in data:
        await answer_service.upsert_answer(
            session, participant.id, answer_body.question_id, answer_body.answer
        )


@router.post(
    "/{challenge_id}/submit", response_model=challenge_schemas.SubmissionResponse
)
async def submit_challenge(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
):
    """
    Supõe-se que todas as respostas do usuário já foram salvas chamando POST /challenge/{challenge_id}/answer.

    Respostas que não foram salvas contam como erradas (recebem pontuação zero).
    """

    participant = await participant_service.get_challenge_participant(
        session, current_user.id, challenge_id, for_update=True
    )

    if participant is None:
        raise BadRequestError("You are not subscribed to this challenge.")

    challenge = await challenge_service.get_challenge_by_id(session, challenge_id)
    if challenge is None:
        raise NotFoundError("Challenge not found")
    if challenge.scoring_type != ChallengeScoringType.QUIZ:
        raise BadRequestError("Manual challenges cannot be submitted by participants.")

    # idempotência: se o usuário já submeteu antes, retorna o valor anterior
    if participant.submitted_at is not None:
        return challenge_schemas.SubmissionResponse(
            submitted_at=participant.submitted_at, score=participant.score
        )

    challenge_service.ensure_challenge_open(challenge.finishes_at)
    score = await challenge_service.process_submission(session, participant, challenge)
    if (
        participant.submitted_at is not None
        and participant.semana_participant is not None
    ):
        await semana_service.add_points(
            session,
            participant.semana_participant,
            score,
            source_type="challenge",
            source_id=participant.id,
            reason=challenge.title,
        )

    return challenge_schemas.SubmissionResponse(
        submitted_at=participant.submitted_at, score=score
    )


@router.get("/{challenge_id}", response_model=challenge_schemas.ChallengeResponse)
async def get_challenge(
    session: Annotated[AsyncSession, Depends(get_session)],
    challenge_id: UUID,
    current_user: Annotated[
        User, Security(get_current_user, scopes=[Scope.PROFILE, Scope.EMAIL])
    ],
) -> challenge_schemas.ChallengeResponse:
    """Retorna informação do challenge, suas perguntas e as respostas atuais do usuário"""

    (
        challenge,
        questions,
        current_answers_by_qid,
        participant,
    ) = await challenge_service.get_challenge_with_context(
        session, challenge_id, current_user.id
    )
    challenge_service.ensure_challenge_open(challenge.finishes_at)

    question_responses = [
        challenge_schemas.QuestionResponse(
            id=q.id,
            prompt=q.prompt,
            current_answer=current_answers_by_qid.get(q.id),
        )
        for q in questions
    ]

    return challenge_schemas.ChallengeResponse(
        id=challenge.id,
        title=challenge.title,
        description=challenge.description,
        prompt=challenge.input.prompt if challenge.input is not None else "",
        scoring_type=challenge.scoring_type,
        image_path=challenge.image_path,
        finishes_at=challenge.finishes_at,
        resource_urls=challenge.resource_urls,
        questions=question_responses,
        is_participant=participant is not None,
        submitted_at=participant.submitted_at if participant else None,
        score=participant.score if participant else None,
    )


@router.get(
    "/{challenge_id}/ranking",
    response_model=list[challenge_schemas.RankingEntry],
)
async def get_ranking(
    session: Annotated[AsyncSession, Depends(get_session)], challenge_id: UUID
):
    """
    Obtém o ranking (Top 10) de um challenge
    """

    participants = await participant_service.get_challenge_ranking(
        session, challenge_id
    )

    return [
        challenge_schemas.RankingEntry(
            id=p.id,
            user_id=p.user_id,
            score=p.score,
            name=p.user.name,
            nickname=(p.semana_participant.nickname if p.semana_participant else ""),
        )
        for p in participants
    ]


@router.get(
    "",
    response_model=Page[challenge_schemas.ChallengePublicResponse],
    include_in_schema=False,
)
@router.get("/", response_model=Page[challenge_schemas.ChallengePublicResponse])
async def list_challenges(
    session: Annotated[AsyncSession, Depends(get_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """
    Obtém todos os challenges, separados por página (definida por limit, offset)
    """

    return await challenge_service.list_challenges_paginated(session, pagination)
