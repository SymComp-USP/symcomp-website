from app.core.exceptions.app_errors import AppError


class UserAlreadyDeletedError(AppError):
    def __init__(self, user_id, headers: dict[str, str] | None = None):
        super().__init__(
            status_code=400,
            type="user_already_deleted",
            title="User already deleted",
            detail=f"User with id {user_id!r} is already deleted.",
            headers=headers,
        )


class UserAlreadyExistsError(AppError):
    def __init__(self, email, headers: dict[str, str] | None = None):
        super().__init__(
            status_code=400,
            type="user_already_exists",
            title="User already exists",
            detail=f"User with email {email!r} already exists.",
            headers=headers,
        )
