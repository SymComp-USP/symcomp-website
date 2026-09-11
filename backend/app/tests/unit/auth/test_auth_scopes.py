from app.auth.scopes import (
    DEFAULT_SCOPES,
    KNOWN_SCOPES,
    SCOPE_DESCRIPTIONS,
    Scope,
)


def test_scope_enum_contains_expected_values():
    assert Scope.OPENID == "openid"
    assert Scope.PROFILE == "profile"
    assert Scope.EMAIL == "email"


def test_scope_descriptions_covers_all_scope_values():
    assert set(SCOPE_DESCRIPTIONS.keys()) == set(Scope)


def test_default_scopes_contains_all_scopes():
    assert set(DEFAULT_SCOPES) == set(Scope)


def test_known_scopes_matches_scope_descriptions():
    assert KNOWN_SCOPES == frozenset(SCOPE_DESCRIPTIONS.keys())


def test_scope_is_str_subclass():
    # Garante que dá pra usar Scope em contextos que esperam str
    assert isinstance(Scope.OPENID, str)
    assert "openid" in {"openid", "profile"}


def test_default_scopes_join_works():
    # create_refresh_token usa " ".join(DEFAULT_SCOPES)
    joined = " ".join(DEFAULT_SCOPES)
    assert "openid" in joined
    assert "profile" in joined
    assert "email" in joined
