"""
Custom exceptions for the application.

This module defines custom exceptions that can be raised by the application
and handled by the global exception handlers.
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(BaseAppException):
    """Exception raised when a database operation fails."""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=500, details=details)


class ConfigurationError(BaseAppException):
    """Exception raised when a configuration value is missing or invalid."""

    def __init__(
        self,
        message: str = "Missing or invalid configuration",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=500, details=details)


class ValidationError(BaseAppException):
    """Exception raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=400, details=details)
