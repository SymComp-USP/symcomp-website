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


class UserNameUpdate(BaseModel):
    # alteração do próprio nome pelo usuário autenticado: nome obrigatório e
    # nenhum outro campo aceito (e-mail, senha e privilégios não podem ser
    # alterados por esta via)
    model_config = ConfigDict(extra="forbid")

    name: Name


class AdminUserCreate(UserCreate):
    # criação feita por um admin: pode definir os privilégios já na criação
    is_admin: bool = False
    is_verified: bool = False


class AdminUserUpdate(UserUpdate):
    # override de admin: além dos campos comuns, pode alterar privilégios.
    # Valores nulos são ignorados (nenhum desses campos aceita NULL no banco).
    is_admin: bool | None = None
    is_verified: bool | None = None


class UserRead(UserBase):
    # Representação pública de um usuário.
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_admin: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class UserMe(UserRead):
    pass
