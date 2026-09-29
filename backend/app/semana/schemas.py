from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SemanaParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    semana_id: int
    user_id: UUID
    nickname: str


class SemanaRankingEntry(BaseModel):
    participant_id: UUID
    nickname: str
    points: int


class SemanaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    ano: int


class PointEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: int
    source_type: str
    source_id: UUID | None
    reason: str | None
    created_at: datetime


class PointAdjustment(BaseModel):
    amount: int
    reason: str
