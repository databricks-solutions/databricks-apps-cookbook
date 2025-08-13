"""V1 API routes."""

from fastapi import APIRouter

from .healthcheck import router as healthcheck_router
from .lakebase import router as lakebase_router
from .orders import router as orders_router
from .tables import router as tables_router

router = APIRouter()

# Include endpoint-specific routers
router.include_router(healthcheck_router)
router.include_router(tables_router)
router.include_router(orders_router)
router.include_router(lakebase_router)
