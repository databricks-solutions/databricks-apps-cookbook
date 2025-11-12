"""
Application settings using Pydantic BaseSettings.

This module defines the application settings that can be set
via environment variables.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Databricks SQL warehouse ID
    databricks_warehouse_id: Optional[str] = Field(
        default=None,
        description="The ID of the Databricks SQL warehouse to connect to",
    )

    # Default values for pagination
    default_limit: int = Field(
        default=100,
        description="Default number of records to return in paginated responses",
    )

    max_limit: int = Field(
        default=1000,
        description="Maximum number of records that can be returned in a single request",
    )

    # Use model_config instead of class Config
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "allow",
    }


# Create a singleton instance of the settings
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings.

    This function is provided as a dependency for FastAPI endpoints.

    Returns:
        The application settings
    """
    return settings
