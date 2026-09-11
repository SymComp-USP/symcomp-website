import jwt

from app.auth.security import (
    create_jwt_token,
    create_random_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.core.config import Settings

# ---------------------------------------------------------------------------
# Senhas
# ---------------------------------------------------------------------------


def test_hash_password_is_salted():
    assert hash_password("same") != hash_password("same")


def test_verify_password_accepts_correct_password():
    hashed = hash_password("my-secret")
    assert verify_password("my-secret", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("my-secret")
    assert verify_password("other", hashed) is False


# ---------------------------------------------------------------------------
# Token opaco
# ---------------------------------------------------------------------------


def test_create_random_token_is_unique():
    assert len({create_random_token() for _ in range(200)}) == 200


def test_create_random_token_has_enough_entropy():
    assert len(create_random_token()) >= 80


def test_hash_token_is_deterministic():
    assert hash_token("abc") == hash_token("abc")


def test_hash_token_changes_with_input():
    assert hash_token("abc") != hash_token("abd")


def test_hash_token_is_sha256_hex():
    digest = hash_token("anything")
    assert len(digest) == 64
    int(digest, 16)


# ---------------------------------------------------------------------------
# create_jwt_token
# ---------------------------------------------------------------------------


def _decode(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.secret_key.get_secret_value(),
        algorithms=[settings.token_algorithm],
    )


def test_create_jwt_token_without_expiry_has_no_exp_or_iat(jwt_settings: Settings):
    token = create_jwt_token({"sub": "x"})
    payload = _decode(token, jwt_settings)

    assert payload["sub"] == "x"
    assert "exp" not in payload
    assert "iat" not in payload


def test_create_jwt_token_with_expiry_adds_exp_and_iat(jwt_settings: Settings):
    token = create_jwt_token({"sub": "x"}, expires_in_minutes=10)
    payload = _decode(token, jwt_settings)

    assert payload["sub"] == "x"
    assert "exp" in payload
    assert "iat" in payload
    # iat deve ser aproximadamente now
    import time

    now = int(time.time())
    assert abs(payload["iat"] - now) <= 5


def test_create_jwt_token_preserves_caller_provided_iat(jwt_settings: Settings):
    custom_iat = 1_000_000_000
    token = create_jwt_token({"sub": "x", "iat": custom_iat}, expires_in_minutes=10)
    payload = _decode(token, jwt_settings)

    assert payload["iat"] == custom_iat


def test_create_jwt_token_preserves_arbitrary_claims(jwt_settings: Settings):
    token = create_jwt_token(
        {"sub": "x", "custom": "value", "nested": {"a": 1}},
        expires_in_minutes=10,
    )
    payload = _decode(token, jwt_settings)

    assert payload["custom"] == "value"
    assert payload["nested"] == {"a": 1}
