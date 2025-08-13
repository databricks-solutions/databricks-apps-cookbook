import asyncio
import logging
import os
import time
import uuid
from typing import AsyncGenerator

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv
from sqlalchemy import URL, event, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
logger = logging.getLogger(__name__)

# Global variables
engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker | None = None
workspace_client: WorkspaceClient | None = None
database_instance = None

# Token management for background refresh
postgres_password: str | None = None
last_password_refresh: float = 0
token_refresh_task: asyncio.Task | None = None


async def refresh_token_background():
    """Background task to refresh tokens every 50 minutes"""
    global postgres_password, last_password_refresh, workspace_client, database_instance

    while True:
        try:
            await asyncio.sleep(50 * 60)  # Wait 50 minutes
            logger.info(
                "Background token refresh: Generating fresh PostgreSQL OAuth token"
            )

            cred = workspace_client.database.generate_database_credential(
                request_id=str(uuid.uuid4()),
                instance_names=[database_instance.name],
            )
            postgres_password = cred.token
            last_password_refresh = time.time()
            logger.info("Background token refresh: Token updated successfully")

        except Exception as e:
            logger.error(f"Background token refresh failed: {e}")


def init_engine():
    """Initialize database connection using SQLAlchemy with automatic token refresh"""
    global \
        engine, \
        AsyncSessionLocal, \
        workspace_client, \
        database_instance, \
        postgres_password, \
        last_password_refresh

    try:
        workspace_client = WorkspaceClient()

        instance_name = os.getenv("LAKEBASE_INSTANCE_NAME")
        if not instance_name:
            raise RuntimeError("LAKEBASE_INSTANCE_NAME environment variable is required")
            
        database_instance = workspace_client.database.get_database_instance(
            name=instance_name
        )

        # Generate initial credentials
        cred = workspace_client.database.generate_database_credential(
            request_id=str(uuid.uuid4()), instance_names=[database_instance.name]
        )
        postgres_password = cred.token
        last_password_refresh = time.time()
        logger.info("Database: Initial credentials generated")

        # Create Engine
        database_name = os.getenv("LAKEBASE_DATABASE_NAME", database_instance.name)
        username = (
            os.getenv("DATABRICKS_CLIENT_ID")
            or workspace_client.current_user.me().user_name
            or None
        )

        url = URL.create(
            drivername="postgresql+asyncpg",
            username=username,
            password="",  # Will be set by event handler
            host=database_instance.read_write_dns,
            port=int(os.getenv("DATABRICKS_DATABASE_PORT", "5432")),
            database=database_name,
        )

        engine = create_async_engine(
            url,
            pool_pre_ping=False,
            echo=False,
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            # OPTIONAL: Recycle connections every hour (before token expires)
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE_INTERVAL", "3600")),
            connect_args={
                "command_timeout": int(os.getenv("DB_COMMAND_TIMEOUT", "10")),
                "server_settings": {
                    "application_name": "fastapi_orders_app",
                },
                "ssl": "require",
            },
        )

        # Register token provider for new connections
        @event.listens_for(engine.sync_engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            global postgres_password
            # Use current token from background refresh
            cparams["password"] = postgres_password

        AsyncSessionLocal = sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info(
            f"Database engine initialized for {database_name} with background token refresh"
        )

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise RuntimeError(f"Failed to initialize database: {e}") from e


async def start_token_refresh():
    """Start the background token refresh task"""
    global token_refresh_task
    if token_refresh_task is None or token_refresh_task.done():
        token_refresh_task = asyncio.create_task(refresh_token_background())
        logger.info("Background token refresh task started")


async def stop_token_refresh():
    """Stop the background token refresh task"""
    global token_refresh_task
    if token_refresh_task and not token_refresh_task.done():
        token_refresh_task.cancel()
        try:
            await token_refresh_task
        except asyncio.CancelledError:
            pass
        logger.info("Background token refresh task stopped")


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with automatic token refresh"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Engine not initialized; call init_engine() first")
    async with AsyncSessionLocal() as session:
        yield session


def check_database_exists() -> bool:
    """Check if the Lakebase database instance exists"""
    try:
        workspace_client = WorkspaceClient()
        instance_name = os.getenv("LAKEBASE_INSTANCE_NAME")
        
        if not instance_name:
            logger.warning("LAKEBASE_INSTANCE_NAME not set - database instance check skipped")
            return False
            
        workspace_client.database.get_database_instance(name=instance_name)
        logger.info(f"Lakebase database instance '{instance_name}' exists")
        return True
    except Exception as e:
        if "not found" in str(e).lower() or "resource not found" in str(e).lower():
            logger.info(f"Lakebase database instance '{instance_name}' does not exist")
        else:
            logger.error(f"Error checking database instance existence: {e}")
        return False


async def database_health() -> bool:
    global engine

    if engine is None:
        logger.error("Database engine failed to initialize.")
        return False

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            logger.info("Database connection is healthy.")
            return True
    except Exception as e:
        logger.error("Database health check failed: %s", e)
        return False
