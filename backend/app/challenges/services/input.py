import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.challenges.models.challenge import Challenge
from app.challenges.models.input import Input


async def get_input_by_challenge_id(
    session: AsyncSession, challenge_id: uuid.UUID
) -> Input | None:
    return await session.scalar(select(Input).where(Input.challenge_id == challenge_id))


async def list_inputs(session: AsyncSession) -> list[Input]:
    result = await session.scalars(select(Input))
    return list(result.all())


async def create_input(
    session: AsyncSession,
    challenge: Challenge,
    prompt: str,
    input_answer: str | None = None,
) -> Input:
    input_data = Input(
        prompt=prompt,
        input_answer=input_answer,
        challenge_id=challenge.id,
    )
    challenge.input = input_data
    session.add(input_data)
    await session.flush()
    return input_data


async def update_input(
    session: AsyncSession,
    input_data: Input,
    *,
    prompt: str | None = None,
    input_answer: str | None = None,
) -> Input:
    if prompt is not None:
        input_data.prompt = prompt
    if input_answer is not None:
        input_data.input_answer = input_answer

    await session.flush()
    return input_data


async def delete_input(session: AsyncSession, input_data: Input) -> None:
    input_data.challenge.input = None
    await session.flush()
