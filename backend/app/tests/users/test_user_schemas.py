from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.users.schemas import UserCreate, UserRead, UserUpdate


def test_user_create_schema_valid():
    data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepassword123",
    }
    user_in = UserCreate(**data)
    assert user_in.email == "test@example.com"
    assert user_in.name == "Test User"
    assert user_in.password == "securepassword123"


def test_user_create_schema_invalid_email():
    data = {
        "email": "invalid-email",
        "name": "Test User",
        "password": "securepassword123",
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_user_read_schema():
    user_id = uuid4()
    now = datetime.now(UTC)
    data = {
        "id": user_id,
        "email": "user@example.com",
        "name": "User Read",
        "is_admin": False,
        "is_verified": True,
        "created_at": now,
        "updated_at": now,
    }
    user_read = UserRead(**data)
    assert user_read.id == user_id
    assert user_read.email == "user@example.com"
    assert user_read.created_at == now


def test_user_update_schema_partial():
    data = {"name": "Updated Name"}
    user_update = UserUpdate(**data)
    assert user_update.name == "Updated Name"
    assert user_update.email is None
