class AppError(Exception):
    """Base exception for application business errors.

    Serves as the root class for the entire hierarchy of custom errors,
    allowing a single exception handler (`app_error_handler`) to catch
    and format any subclass consistently, following the RFC 7807 standard
    (Problem Details for HTTP APIs).

    Attributes:
        status_code: HTTP status code corresponding to the error.
        type: Short, stable identifier for the error type, used as part
            of the API contract (should not change without versioning).
        title: Short, human-readable description of the error, fixed for
            the same type.
        detail: Explanation specific to this occurrence of the error.
    """

    def __init__(self, status_code: int, type: str, title: str, detail: str):
        self.status_code = status_code
        self.type = type
        self.title = title
        self.detail = detail
        super().__init__(detail)


class BadRequestError(AppError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=400, type="bad_request", title="Bad request", detail=detail
        )


class UnauthorizedError(AppError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=401, type="unauthorized", title="Unauthorized", detail=detail
        )


class ForbiddenError(AppError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=403, type="forbidden", title="Forbidden", detail=detail
        )


class NotFoundError(AppError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=404, type="not_found", title="Resource not found", detail=detail
        )


class InternalServerError(AppError):
    def __init__(self, detail: str):
        super().__init__(
            status_code=500,
            type="internal_server_error",
            title="Internal server error",
            detail=detail,
        )
