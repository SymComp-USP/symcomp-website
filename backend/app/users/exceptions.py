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


class NoAvailableUsername(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            type="no_available_username",
            title="No available username",
            detail="No usernames available for the user.",
        )


class CouldNotAssignUsernameError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=500,
            type="could_not_assign_username",
            title="Could not assign username",
            detail="Could not assign a username. Try again later.",
        )
