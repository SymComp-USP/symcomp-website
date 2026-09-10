from app.auth.security import (
    create_random_token,
    hash_password,
    hash_token,
    verify_password,
)

# ===========================================================================
# hash_password / verify_password
# ===========================================================================


def test_hash_password_is_salted():
    assert hash_password("same") != hash_password("same")


def test_verify_password_accepts_correct_password():
    hashed = hash_password("my-secret")
    assert verify_password("my-secret", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("my-secret")
    assert verify_password("other", hashed) is False


# ===========================================================================
# create_random_token
# ===========================================================================


def test_create_random_token_is_unique():
    tokens = {create_random_token() for _ in range(200)}
    assert len(tokens) == 200


def test_create_random_token_has_enough_entropy():
    # token_urlsafe(64) gera ~86 chars
    assert len(create_random_token()) >= 80


# ===========================================================================
# hash_token
# ===========================================================================


def test_hash_token_is_deterministic():
    assert hash_token("abc") == hash_token("abc")


def test_hash_token_changes_with_input():
    assert hash_token("abc") != hash_token("abd")


def test_hash_token_is_sha256_hex():
    digest = hash_token("anything")
    assert len(digest) == 64
    int(digest, 16)  # levanta se não for hex
