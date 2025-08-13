"""V1 API routes."""

import logging
from fastapi import APIRouter

from .healthcheck import router as healthcheck_router
from .lakebase import router as lakebase_router

logger = logging.getLogger(__name__)


def create_router(database_exists: bool = False) -> APIRouter:
    """Create API router with conditional endpoint registration"""
    router = APIRouter()
    
    # Always include these endpoints
    router.include_router(healthcheck_router)
    router.include_router(lakebase_router)
    
    # Conditionally include database-dependent endpoints
    if database_exists:
        try:
            from .orders import router as orders_router
            from .tables import router as tables_router
            
            router.include_router(tables_router)
            router.include_router(orders_router)
            logger.info("Database-dependent endpoints (orders, tables) registered successfully")
        except Exception as e:
            logger.error(f"Failed to register database-dependent endpoints: {e}")
    else:
        logger.info("Database instance not found - skipping orders and tables endpoints")
        logger.info("Create Lakebase resources using POST /api/v1/resources/create-lakebase-resources")
    
    return router
