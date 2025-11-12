"""
Main FastAPI application.

This module creates and configures the FastAPI application.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict

import uvicorn
from config.database import (
    check_database_exists,
    database_health,
    init_engine,
    start_token_refresh,
    stop_token_refresh,
)
from errors.handlers import register_exception_handlers
from routes import api_router
from services.db.connector import close_connections
from sqlmodel import SQLModel

from fastapi import FastAPI, Request

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("Application startup initiated")
    
    # Check if database exists before initializing
    database_exists = check_database_exists()
    health_check_task = None
    
    if database_exists:
        try:
            init_engine()
            from config.database import engine

            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            await start_token_refresh()
            health_check_task = asyncio.create_task(check_database_health(300))
            logger.info("Database engine initialized and health monitoring started")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            logger.info("Application will start without database functionality")
    else:
        logger.info("No Lakebase database instance found - starting with limited functionality")
        logger.info("Use POST /api/v1/resources/create-lakebase-resources to create database resources")
    
    logger.info("Application startup complete")

    yield

    logger.info("Application shutdown initiated")
    if health_check_task:
        health_check_task.cancel()
        try:
            await health_check_task
        except asyncio.CancelledError:
            logger.info("Database health check task cancelled successfully")
        await stop_token_refresh()
    logger.info("Application shutdown complete")
    close_connections()


# Create the main FastAPI application
app = FastAPI(
    title="FastAPI & Databricks Apps",
    description="A simple FastAPI application example for Databricks Apps runtime",
    version="1.0.0",
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# Include the API router
app.include_router(api_router)


# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "app": "Databricks FastAPI Example",
        "message": "Welcome to the Databricks FastAPI example app",
        "docs": "/docs",
    }


# Performance monitoring middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(
        f"Request: {request.method} {request.url.path} - {process_time * 1000:.1f}ms"
    )
    return response


async def check_database_health(interval: int):
    while True:
        try:
            is_healthy = await database_health()
            if not is_healthy:
                logger.warning(
                    "Database Health check failed. Connection is not healthy."
                )
        except Exception as e:
            logger.error(f"Exception during health check: {e}")
        await asyncio.sleep(interval)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
