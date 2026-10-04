"""Create a repeatable local dataset for exercising the active app flows.

Run from ``backend/`` with ``uv run python -m scripts.seed_mock_data``.
Seeded accounts use the password ``local-test-password``. This script refuses to
run when ``APP_ENV=prod`` and never deletes existing rows.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.atividade.models import Atividade, Presenca, StatusAtividade, TipoAtividade
from app.auth.security import hash_password
from app.challenges.models.answer import Answer
from app.challenges.models.challenge import Challenge, ChallengeScoringType
from app.challenges.models.challenge_participant import ChallengeParticipant
from app.challenges.models.input import Input
from app.challenges.models.question import Question
from app.core.config import AppEnv, get_settings
from app.core.database import create_database
from app.semana.models import PointEvent, SemanaEvent, SemanaParticipant
from app.users.models import User

SEED_PASSWORD = "local-test-password"

USER_SPECS = {
    "admin": {
        "email": "seed-admin@example.com",
        "name": "Mock Admin",
        "is_admin": True,
    },
    "alice": {
        "email": "alice@example.com",
        "name": "Alice Almeida",
        "is_admin": False,
    },
    "bruno": {
        "email": "bruno@example.com",
        "name": "Bruno Barbosa",
        "is_admin": False,
    },
    "carla": {
        "email": "carla@example.com",
        "name": "Carla Costa",
        "is_admin": False,
    },
}


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    settings = get_settings()
    if settings.app_env == AppEnv.production:
        raise RuntimeError("Mock data cannot be seeded when APP_ENV=prod.")

    engine, session_factory = create_database(settings)
    try:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        await engine.dispose()


async def get_or_create_user(session: AsyncSession, spec: dict[str, Any]) -> User:
    user = await session.scalar(select(User).where(User.email == spec["email"]))
    if user is None:
        legacy_email = spec["email"].replace("@example.com", "@example.test")
        user = await session.scalar(select(User).where(User.email == legacy_email))
    if user is None:
        user = User(
            email=spec["email"],
            name=spec["name"],
            password_hash=hash_password(SEED_PASSWORD),
            is_admin=spec["is_admin"],
            is_verified=True,
        )
        session.add(user)
        await session.flush()
    else:
        user.email = spec["email"]
        user.name = spec["name"]
        user.is_admin = spec["is_admin"]
        user.is_verified = True
        user.deleted_at = None
        await session.flush()
    return user


async def get_or_create_week(
    session: AsyncSession, name: str, year: int
) -> SemanaEvent:
    week = await session.scalar(
        select(SemanaEvent).where(SemanaEvent.ano == year, SemanaEvent.nome == name)
    )
    if week is None:
        week = SemanaEvent(nome=name, ano=year)
        session.add(week)
    else:
        week.nome = name
    await session.flush()
    return week


async def get_or_create_challenge(
    session: AsyncSession,
    week: SemanaEvent,
    *,
    title: str,
    description: str,
    scoring_type: ChallengeScoringType,
    points_value: int,
) -> Challenge:
    challenge = await session.scalar(
        select(Challenge).where(
            Challenge.semana_id == week.id,
            Challenge.title == title,
            Challenge.deleted_at.is_(None),
        )
    )
    if challenge is None:
        challenge = Challenge(title=title, semana_id=week.id)
        session.add(challenge)

    challenge.description = description
    challenge.scoring_type = scoring_type
    challenge.points_value = points_value
    challenge.finishes_at = datetime.now(UTC) + timedelta(days=30)
    await session.flush()
    return challenge


async def get_or_create_week_participant(
    session: AsyncSession,
    week: SemanaEvent,
    user: User,
    nickname: str,
) -> SemanaParticipant:
    participant = await session.scalar(
        select(SemanaParticipant).where(
            SemanaParticipant.semana_id == week.id,
            SemanaParticipant.user_id == user.id,
        )
    )
    if participant is None:
        participant = SemanaParticipant(
            semana_id=week.id,
            user_id=user.id,
            nickname=nickname,
        )
        session.add(participant)
    else:
        participant.nickname = nickname
        participant.deleted_at = None
    await session.flush()
    return participant


async def get_or_create_challenge_participant(
    session: AsyncSession,
    user: User,
    challenge: Challenge,
    week_participant: SemanaParticipant,
    *,
    score: int,
    submission: str | None,
    submitted_at: datetime | None,
) -> ChallengeParticipant:
    participant = await session.scalar(
        select(ChallengeParticipant).where(
            ChallengeParticipant.user_id == user.id,
            ChallengeParticipant.challenge_id == challenge.id,
        )
    )
    if participant is None:
        participant = ChallengeParticipant(
            user_id=user.id,
            challenge_id=challenge.id,
        )
        session.add(participant)

    participant.semana_participant_id = week_participant.id
    participant.score = score
    participant.submission = submission
    participant.submitted_at = submitted_at
    participant.deleted_at = None
    await session.flush()
    return participant


async def get_or_create_question(
    session: AsyncSession,
    challenge: Challenge,
    prompt: str,
    answer: str,
) -> Question:
    question = await session.scalar(
        select(Question).where(
            Question.challenge_id == challenge.id,
            Question.prompt == prompt,
        )
    )
    if question is None:
        question = Question(
            challenge_id=challenge.id,
            prompt=prompt,
            answer=answer,
        )
        session.add(question)
    else:
        question.answer = answer
    await session.flush()
    return question


async def get_or_create_answer(
    session: AsyncSession,
    participant: ChallengeParticipant,
    question: Question,
    content: str,
    is_correct: bool,
) -> Answer:
    answer = await session.scalar(
        select(Answer).where(
            Answer.participant_id == participant.id,
            Answer.question_id == question.id,
        )
    )
    if answer is None:
        answer = Answer(
            participant_id=participant.id,
            question_id=question.id,
            content=content,
            is_correct=is_correct,
        )
        session.add(answer)
    else:
        answer.content = content
        answer.is_correct = is_correct
        answer.deleted_at = None
    await session.flush()
    return answer


async def get_or_create_input(
    session: AsyncSession, challenge: Challenge, prompt: str, expected_answer: str
) -> Input:
    input_data = await session.scalar(
        select(Input).where(Input.challenge_id == challenge.id)
    )
    if input_data is None:
        input_data = Input(challenge_id=challenge.id, prompt=prompt)
        session.add(input_data)
    input_data.prompt = prompt
    input_data.input_answer = expected_answer
    await session.flush()
    return input_data


async def get_or_create_activity(
    session: AsyncSession,
    week: SemanaEvent,
    *,
    code: str,
    kind: TipoAtividade,
    title: str,
    start: datetime,
    end: datetime,
    points: int,
    hours: int,
    status: StatusAtividade = StatusAtividade.CONFIRMADA,
) -> Atividade:
    activity = await session.scalar(
        select(Atividade).where(
            Atividade.semana_id == week.id,
            Atividade.codigo == code,
        )
    )
    if activity is None:
        activity = Atividade(semana_id=week.id, codigo=code, tipo=kind)
        session.add(activity)

    activity.tipo = kind
    activity.titulo = title
    activity.descricao = f"Mock schedule entry for {title}."
    activity.local = "Auditório principal"
    activity.palestrantes = [
        {"nome": "Equipe SymComp", "sobre": "Palestrante de teste."}
    ]
    activity.link_live = None
    activity.status = status
    activity.comeca_as = start
    activity.termina_as = end
    activity.pontos = points
    activity.horas = hours
    await session.flush()
    return activity


async def get_or_create_presence(
    session: AsyncSession,
    activity: Atividade,
    *,
    user: User | None,
    name: str,
    email: str,
    hours: int,
) -> Presenca:
    presence = await session.scalar(
        select(Presenca).where(
            Presenca.atividade_id == activity.id,
            Presenca.email == email,
        )
    )
    if presence is None:
        legacy_email = email.replace("@example.com", "@example.test")
        presence = await session.scalar(
            select(Presenca).where(
                Presenca.atividade_id == activity.id,
                Presenca.email == legacy_email,
            )
        )
    if presence is None:
        presence = Presenca(
            atividade_id=activity.id,
            user_id=user.id if user else None,
            nome=name,
            email=email,
            horas=hours,
        )
        session.add(presence)
    else:
        presence.user_id = user.id if user else None
        presence.nome = name
        presence.email = email
        presence.horas = hours
    await session.flush()
    return presence


async def get_or_create_point_event(
    session: AsyncSession,
    week_participant: SemanaParticipant,
    *,
    amount: int,
    source_type: str,
    source_id,
    reason: str,
) -> PointEvent:
    event = await session.scalar(
        select(PointEvent).where(
            PointEvent.semana_participant_id == week_participant.id,
            PointEvent.source_type == source_type,
            PointEvent.source_id == source_id,
        )
    )
    if event is None:
        event = PointEvent(
            semana_participant_id=week_participant.id,
            source_type=source_type,
            source_id=source_id,
        )
        session.add(event)
    event.amount = amount
    event.reason = reason
    await session.flush()
    return event


async def seed() -> None:
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)

    async with session_scope() as session:
        users = {
            key: await get_or_create_user(session, spec)
            for key, spec in USER_SPECS.items()
        }
        weeks = {
            2025: await get_or_create_week(session, "Semana Mock Arquivada", 2025),
            2026: await get_or_create_week(session, "Semana Mock 2026", 2026),
        }

        week_participants: dict[tuple[int, str], SemanaParticipant] = {}
        for year, week in weeks.items():
            for key, user in users.items():
                if key == "admin":
                    continue
                week_participants[(year, key)] = await get_or_create_week_participant(
                    session,
                    week,
                    user,
                    nickname=f"{key}{year}",
                )

        quiz = await get_or_create_challenge(
            session,
            weeks[2026],
            title="Mock: Quiz de fundamentos",
            description="Perguntas de teste com diferentes níveis de acerto.",
            scoring_type=ChallengeScoringType.QUIZ,
            points_value=100,
        )
        input_challenge = await get_or_create_challenge(
            session,
            weeks[2026],
            title="Mock: Resposta livre",
            description="Desafio de entrada com resposta automática.",
            scoring_type=ChallengeScoringType.INPUT,
            points_value=80,
        )
        manual_challenge = await get_or_create_challenge(
            session,
            weeks[2026],
            title="Mock: Avaliação manual",
            description="Pontuação atribuída pela equipe.",
            scoring_type=ChallengeScoringType.MANUAL,
            points_value=50,
        )
        await get_or_create_input(
            session,
            input_challenge,
            prompt="Qual é a palavra-chave do evento?",
            expected_answer="symcomp",
        )

        questions = [
            await get_or_create_question(session, quiz, "Quanto é 2 + 2?", "4"),
            await get_or_create_question(
                session, quiz, "Qual linguagem roda no navegador?", "JavaScript"
            ),
        ]
        quiz_participants: dict[str, ChallengeParticipant] = {}
        quiz_answers = {
            "alice": [("4", True), ("JavaScript", True)],
            "bruno": [("4", True), ("Python", False)],
            "carla": [("5", False), ("Python", False)],
        }
        for key, answers in quiz_answers.items():
            score = sum(50 for _, is_correct in answers if is_correct)
            participant = await get_or_create_challenge_participant(
                session,
                users[key],
                quiz,
                week_participants[(2026, key)],
                score=score,
                submission=None,
                submitted_at=now - timedelta(hours=2),
            )
            quiz_participants[key] = participant
            for question, (content, is_correct) in zip(questions, answers, strict=True):
                await get_or_create_answer(
                    session, participant, question, content, is_correct
                )

        input_attempts = {
            "alice": ("symcomp", 80),
            "bruno": ("wrong-answer", 0),
        }
        input_participants: dict[str, ChallengeParticipant] = {}
        for key, (submission, score) in input_attempts.items():
            input_participants[key] = await get_or_create_challenge_participant(
                session,
                users[key],
                input_challenge,
                week_participants[(2026, key)],
                score=score,
                submission=submission,
                submitted_at=now - timedelta(hours=1),
            )

        manual_participant = await get_or_create_challenge_participant(
            session,
            users["carla"],
            manual_challenge,
            week_participants[(2026, "carla")],
            score=17,
            submission=None,
            submitted_at=None,
        )

        for key, participant in quiz_participants.items():
            await get_or_create_point_event(
                session,
                week_participants[(2026, key)],
                amount=participant.score,
                source_type="challenge",
                source_id=participant.id,
                reason=quiz.title,
            )
        for key, participant in input_participants.items():
            await get_or_create_point_event(
                session,
                week_participants[(2026, key)],
                amount=participant.score,
                source_type="challenge",
                source_id=participant.id,
                reason=input_challenge.title,
            )
        await get_or_create_point_event(
            session,
            week_participants[(2026, "carla")],
            amount=manual_participant.score,
            source_type="manual_adjustment",
            source_id=manual_participant.id,
            reason="Mock manual score adjustment",
        )

        activities = [
            await get_or_create_activity(
                session,
                weeks[2026],
                code="1001",
                kind=TipoAtividade.PALESTRA,
                title="Mock: Abertura e computação",
                start=now + timedelta(days=1),
                end=now + timedelta(days=1, hours=1),
                points=10,
                hours=1,
            ),
            await get_or_create_activity(
                session,
                weeks[2026],
                code="1002",
                kind=TipoAtividade.WORKSHOP,
                title="Mock: Laboratório de programação",
                start=now + timedelta(days=1, hours=2),
                end=now + timedelta(days=1, hours=4),
                points=25,
                hours=2,
                status=StatusAtividade.PROVISORIA,
            ),
            await get_or_create_activity(
                session,
                weeks[2025],
                code="1003",
                kind=TipoAtividade.COFFEE_BREAK,
                title="Mock: Intervalo arquivado",
                start=now - timedelta(days=300),
                end=now - timedelta(days=300) + timedelta(minutes=30),
                points=5,
                hours=1,
            ),
        ]

        attendance_specs = [
            (activities[0], 2026, "alice", users["alice"], 1),
            (activities[0], 2026, "bruno", users["bruno"], 1),
            (activities[1], 2026, "carla", users["carla"], 2),
            (activities[2], 2025, None, None, 1),
        ]
        for activity, year, user_key, user, hours in attendance_specs:
            name = user.name if user is not None else "Visitante Mock"
            email = user.email if user is not None else "visitor@example.com"
            presence = await get_or_create_presence(
                session,
                activity,
                user=user,
                name=name,
                email=email,
                hours=hours,
            )
            if user_key is not None:
                await get_or_create_point_event(
                    session,
                    week_participants[(year, user_key)],
                    amount=activity.pontos,
                    source_type="activity",
                    source_id=presence.id,
                    reason=activity.titulo,
                )

        print("Mock dataset ready.")
        print(f"Admin: {USER_SPECS['admin']['email']} / {SEED_PASSWORD}")
        for year, week in weeks.items():
            print(f"Semana {year}: {week.id} ({week.nome})")
        print("Challenges:")
        for challenge in (quiz, input_challenge, manual_challenge):
            print(f"  {challenge.id} {challenge.scoring_type.value}: {challenge.title}")
        print("Activities:")
        for activity in activities:
            print(f"  {activity.id} {activity.codigo}: {activity.titulo}")


async def main() -> None:
    await seed()


if __name__ == "__main__":
    asyncio.run(main())
