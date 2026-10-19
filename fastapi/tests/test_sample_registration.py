"""The sample's database routes must register, and the sample must install what its async engine needs."""

import re
from pathlib import Path

FASTAPI_DIR = Path(__file__).resolve().parents[1]


def test_orders_model_uses_public_schema():
    """`__table_args__` must be a dict; a bare string makes SQLAlchemy raise ArgumentError at import."""
    from models.orders import Order

    assert Order.__table__.schema == "public"


def test_database_routers_register():
    """With a database, the orders and tables routes must be served, not skipped by the import guard."""
    from fastapi import FastAPI
    from routes.v1 import create_router

    app = FastAPI()
    app.include_router(create_router(database_exists=True))
    paths = set(app.openapi()["paths"])
    assert {"/count", "/table"} <= paths, sorted(paths)


def test_requirements_install_greenlet():
    """The async engine needs greenlet; `sqlalchemy[asyncio]` installs it on every platform."""
    lines = (FASTAPI_DIR / "requirements.txt").read_text().splitlines()
    sqlalchemy = [line for line in lines if re.match(r"\s*sqlalchemy\b", line, re.I)]
    assert sqlalchemy and all("[asyncio]" in line for line in sqlalchemy), sqlalchemy
