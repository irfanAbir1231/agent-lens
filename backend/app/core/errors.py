from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_request_id
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)
HTTP_422_STATUS = (
    status.HTTP_422_UNPROCESSABLE_CONTENT
    if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT")
    else 422
)


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundError(AppError):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
            message=message,
            details=details,
        )


def build_error_response(
    *,
    code: str,
    message: str,
    status_code: int,
    details: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    payload = ErrorResponse(
        code=code,
        message=message,
        details=details,
        request_id=request_id or get_request_id(),
    )
    return JSONResponse(
        status_code=status_code, content=payload.model_dump(mode="json")
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return build_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return build_error_response(
                code="route_not_found",
                message="The requested resource was not found.",
                status_code=exc.status_code,
                details={"path": request.url.path},
            )

        return build_error_response(
            code="http_error",
            message="The request could not be completed.",
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            {"location": "/".join(map(str, error["loc"])), "message": error["msg"]}
            for error in exc.errors()
        ]
        return build_error_response(
            code="request_validation_error",
            message="The request could not be validated.",
            status_code=HTTP_422_STATUS,
            details=details,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc)
        return build_error_response(
            code="internal_server_error",
            message="An unexpected error occurred.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
