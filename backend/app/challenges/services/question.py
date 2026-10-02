import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges import schemas as challenge_schemas
from app.challenges.models.challenge import Challenge
from app.challenges.models.question import Question


async def get_question_by_id_and_challenge(
    session: AsyncSession,
    question_id: uuid.UUID,
    challenge_id: uuid.UUID,
) -> Question | None:
    return await session.scalar(
        select(Question).where(
            Question.id == question_id,
            Question.challenge_id == challenge_id,
        )
    )


async def list_questions(
    session: AsyncSession, challenge_id: uuid.UUID | None = None
) -> list[Question]:

    query = select(Question)

    if challenge_id is not None:
        query = query.where(Question.challenge_id == challenge_id)

    result = await session.execute(query)
    return list(result.scalars().all())


async def create_question(
    session: AsyncSession,
    prompt: str,
    answer: str,
    challenge_id: uuid.UUID,
) -> Question:

    question = Question(
        prompt=prompt,
        answer=answer,
        challenge_id=challenge_id,
    )

    session.add(question)
    await session.flush()
    return question


async def replace_challenge_questions(
    session: AsyncSession,
    challenge: Challenge,
    questions: list[challenge_schemas.QuestionCreate],
) -> list[Question]:
    await session.execute(delete(Question).where(Question.challenge_id == challenge.id))
    await session.flush()
    await session.refresh(challenge, attribute_names=["questions"])

    replacement_questions = [
        Question(
            prompt=question.prompt,
            answer=question.answer,
            challenge_id=challenge.id,
        )
        for question in questions
    ]
    session.add_all(replacement_questions)
    await session.flush()
    await session.refresh(challenge, attribute_names=["questions"])
    return replacement_questions


async def update_question(
    session: AsyncSession,
    question: Question,
    prompt: str | None = None,
    answer: str | None = None,
) -> Question:
    if prompt is not None:
        question.prompt = prompt
    if answer is not None:
        question.answer = answer
    await session.flush()
    return question


async def delete_question(session: AsyncSession, question: Question) -> None:
    await session.delete(question)
    await session.flush()
