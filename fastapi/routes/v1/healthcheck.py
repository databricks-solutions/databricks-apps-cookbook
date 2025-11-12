"""Healthcheck endpoint for the V1 API."""

from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck() -> Dict[str, str]:
    """Return the API status."""
    return {"status": "OK", "timestamp": datetime.now(timezone.utc).isoformat()}
