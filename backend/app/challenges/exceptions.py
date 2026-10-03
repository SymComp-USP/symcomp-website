from app.core.exceptions.app_errors import (
    AppError,
)


class AlreadyDeletedError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            type="already_deleted",
            title="Already deleted",
            detail="Resource is already deleted",
        )


class ChallengeClosedError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            type="challenge_closed",
            title="Challenge closed",
            detail="This challenge has ended and no longer accepts answers or submissions.",
        )


class ChallengeNotStartedError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            type="challenge_not_started",
            title="Challenge not started",
            detail="This challenge has not started yet.",
        )
