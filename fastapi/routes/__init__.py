"""Routes package for the FastAPI application."""

from fastapi import APIRouter
from config.database import check_database_exists

# Import router factory from versioned packages
from .v1 import create_router

# Check if database exists and create appropriate router
database_exists = check_database_exists()
v1_router = create_router(database_exists=database_exists)

# Create a router for the API
api_router = APIRouter()

# Include versioned routers - prefix must have /api for Databricks Apps token-based auth
api_router.include_router(v1_router, prefix="/api/v1")
