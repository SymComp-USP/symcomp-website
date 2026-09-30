from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.atividade.models import StatusAtividade, TipoAtividade


class AtividadeCreate(BaseModel):
    tipo: TipoAtividade
    titulo: str = ""
    descricao: str | None = None
    local: str | None = None
    palestrantes: list[dict[str, str]] = Field(default_factory=list)
    link_live: str | None = None
    comeca_as: datetime
    termina_as: datetime
    status: StatusAtividade = StatusAtividade.PROVISORIA
    pontos: int = Field(default=0, ge=0)
    horas: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.termina_as <= self.comeca_as:
            raise ValueError("termina_as must be after comeca_as")
        return self


class AtividadeUpdate(BaseModel):
    tipo: TipoAtividade | None = None
    titulo: str | None = None
    descricao: str | None = None
    local: str | None = None
    palestrantes: list[dict[str, str]] | None = None
    link_live: str | None = None
    comeca_as: datetime | None = None
    termina_as: datetime | None = None
    status: StatusAtividade | None = None
    pontos: int | None = Field(default=None, ge=0)
    horas: int | None = Field(default=None, ge=1)


class AtividadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    semana_id: int
    tipo: TipoAtividade
    titulo: str
    descricao: str | None
    local: str | None
    palestrantes: list[dict[str, str]]
    link_live: str | None
    status: StatusAtividade
    comeca_as: datetime
    termina_as: datetime
    codigo: str
    pontos: int
    horas: int


class PresencaRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None


class PresencaResponse(BaseModel):
    atividade_id: UUID
    registrada: bool = True
    pontos_adicionados: int
    horas: int


class AdminPresencaCreate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr


class AdminPresencaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    atividade_id: UUID
    user_id: UUID | None
    nome: str
    email: EmailStr
    horas: int
