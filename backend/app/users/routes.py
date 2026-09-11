from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.users import services
from app.users.schemas import UserCreate

router = APIRouter(tags=["user"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def signup_with_password(
    db_session: Annotated[AsyncSession, Depends(get_session)], user_info: UserCreate
):
    user = await services.create_user(db_session, user_info)

    return user
