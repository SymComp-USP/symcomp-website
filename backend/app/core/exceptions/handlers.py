from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.exceptions.app_errors import AppError, InternalServerError


class ApiErrorResponse(BaseModel):
    """Standardized error response schema for the API.

    Follows the RFC 7807 structure (Problem Details for HTTP APIs), ensuring
    that every error returned by the API has a consistent, documentable JSON
    format in OpenAPI/Swagger.

    Attributes:
        type: URI or identifier for the error type.
        title: Short, human-readable description, fixed for the same error type.
        status: HTTP status code of the error.
        detail: Explanation specific to this occurrence of the error.
        instance: Path of the request that caused the error, when available.
    """

    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None


async def app_error_handler(request: Request, error: Exception):
    assert isinstance(error, AppError)

    body = ApiErrorResponse(
        type=error.type,
        title=error.title,
        status=error.status_code,
        detail=error.detail,
        instance=str(request.url.path),
    )

    return JSONResponse(
        status_code=body.status,
        content=body.model_dump(exclude_none=True),
        headers=error.headers,
    )


async def exception_handler(request: Request, _: Exception):
    error = InternalServerError("An unexpected error occurred.")

    body = ApiErrorResponse(
        type=error.type,
        title=error.title,
        status=error.status_code,
        detail=error.detail,
        instance=str(request.url.path),
    )

    return JSONResponse(
        status_code=body.status, content=body.model_dump(exclude_none=True)
    )
