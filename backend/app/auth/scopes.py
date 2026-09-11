# app/auth/scopes.py
from enum import StrEnum


class Scope(StrEnum):
    OPENID = "openid"
    PROFILE = "profile"
    EMAIL = "email"


SCOPE_DESCRIPTIONS: dict[str, str] = {
    Scope.OPENID: "Indica o uso do protocolo OpenID Connect",
    Scope.PROFILE: "Permite ler dados básicos do usuário (nome, id)",
    Scope.EMAIL: "Permite ler o endereço de e-mail do usuário",
}

DEFAULT_SCOPES: list[str] = [Scope.OPENID, Scope.PROFILE, Scope.EMAIL]

KNOWN_SCOPES: frozenset[str] = frozenset(SCOPE_DESCRIPTIONS.keys())
