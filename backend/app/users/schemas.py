import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

# tipos uteis reutilizáveis
Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
]
Password = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=8, max_length=128)
]


class UserBase(BaseModel):
    email: EmailStr
    name: Name


class UserCreate(UserBase):
    # criação de usuario por vias convencionais, senha obrigatória
    password: Password


class UserUpdate(BaseModel):
    # atualização de dados, apenas campos explicitamente enviados são considerados
    email: EmailStr | None = None
    name: Name | None = None
    password: Password | None = None


class UserRead(UserBase):
    # Representação pública de um usuário.
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_admin: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
