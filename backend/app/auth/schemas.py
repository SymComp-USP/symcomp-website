from uuid import UUID

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    id_token: str | None = None
    token_type: str


class TokenData(BaseModel):
    user_id: UUID | None = None
    scopes: list[str] = Field(default_factory=list)


class RequestedScopesBody(BaseModel):
    requested_scopes: list[str] | None = None


class RotationResult(BaseModel):
    access_token: str
    refresh_token: str
