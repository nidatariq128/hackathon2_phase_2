# Task: T-013 - Create Main FastAPI Application
# Spec: specs/task-crud/spec.md
# Plan: specs/task-crud/plan.md
"""
Custom exception handlers for the FastAPI application.

Provides consistent error response format across all endpoints.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    status_code: int


class ValidationErrorDetail(BaseModel):
    """Validation error detail model."""
    field: str
    message: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    detail: str
    errors: list[ValidationErrorDetail]


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors with consistent format.

        Transforms validation errors into a user-friendly format
        with field names and error messages.
        """
        errors = []
        for error in exc.errors():
            # Build field path from location tuple
            field_path = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """
        Handle HTTP exceptions with consistent format.

        Ensures all HTTP errors have a consistent response structure.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Handle unexpected exceptions.

        Catches any unhandled exceptions and returns a generic error
        message without exposing internal details.
        """
        # Log the actual error for debugging (in production, use proper logging)
        print(f"Unhandled exception: {exc}")

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "status_code": 500,
            },
        )
