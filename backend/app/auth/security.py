import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import get_settings

# --- funções de autenticação ---
# Inicialização da biblioteca de hash
ph = PasswordHash((Argon2Hasher(),))


# Função de criar hash
def hash_password(password: str) -> str:
    return ph.hash(password)


# Função de verificação da hash
def verify_password(plain_password, hashed_password):
    return ph.verify(plain_password, hashed_password)


def create_random_token():
    return secrets.token_urlsafe(64)


def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


def create_jwt_token(data: dict, expires_in_minutes: int | None = None) -> str:
    settings = get_settings()

    SECRET_KEY = settings.secret_key.get_secret_value()
    TOKEN_ALGORITHM = settings.token_algorithm

    to_encode = data.copy()

    if expires_in_minutes is not None:
        now = datetime.now(UTC)
        to_encode.setdefault("iat", int(now.timestamp()))
        to_encode["exp"] = int(
            (now + timedelta(minutes=expires_in_minutes)).timestamp()
        )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
    return encoded_jwt
