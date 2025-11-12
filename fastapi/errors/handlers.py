"""
Exception handlers for the application.

This module defines handlers for exceptions that can be registered
with FastAPI to provide consistent error responses.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    BaseAppException,
    DatabaseError,
    ConfigurationError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application
    """

    @app.exception_handler(BaseAppException)
    async def handle_base_app_exception(
        request: Request, exc: BaseAppException
    ) -> JSONResponse:
        """Handle BaseAppException and its subclasses."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(PydanticValidationError)
    async def handle_validation_error(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "Validation error",
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error",
                "details": {"type": str(type(exc).__name__), "info": str(exc)},
            },
        )
