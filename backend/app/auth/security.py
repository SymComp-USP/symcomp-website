import hashlib
import secrets

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

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
