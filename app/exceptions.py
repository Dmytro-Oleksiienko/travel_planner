"""Custom exceptions and exception handlers for the application."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: int | str):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id {resource_id} not found",
        )


class ConflictException(AppException):
    """Conflict - action cannot be performed."""

    def __init__(self, detail: str):
        super().__init__(status_code=409, detail=detail)


class BadRequestException(AppException):
    """Bad request - invalid input."""

    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class ExternalAPIException(AppException):
    """Error communicating with external API."""

    def __init__(self, detail: str):
        super().__init__(status_code=502, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
