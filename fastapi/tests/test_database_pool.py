"""Pool settings: a connection the server closed must be replaced, and no connection may outlive its token."""

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import config.database as database

TOKEN_LIFE_SECONDS = 3600
FASTAPI_DIR = Path(__file__).resolve().parents[1]


class FakeWorkspace:
    def __init__(self):
        self.database = SimpleNamespace(
            get_database_instance=lambda name: SimpleNamespace(name=name, read_write_dns="db.example.com"),
            generate_database_credential=lambda **kw: SimpleNamespace(token="fake-token"),
        )
        self.current_user = SimpleNamespace(me=lambda: SimpleNamespace(user_name="stub-user@example.com"))


@pytest.fixture
def engine_kwargs(monkeypatch):
    """Run init_engine() with a fake workspace and return the kwargs it passed to create_async_engine."""
    for name in ("DB_POOL_PRE_PING", "DB_POOL_RECYCLE_INTERVAL", "DB_CONNECT_TIMEOUT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LAKEBASE_INSTANCE_NAME", "test-instance")
    monkeypatch.setattr(database, "WorkspaceClient", FakeWorkspace)
    captured = {}
    real_create = database.create_async_engine

    def capture(url, **kwargs):
        captured.update(kwargs)
        return real_create(url, **kwargs)

    monkeypatch.setattr(database, "create_async_engine", capture)

    def run():
        captured.clear()
        database.init_engine()
        return dict(captured)

    return run


def test_defaults_replace_dead_connections_and_recycle_before_token_expiry(engine_kwargs):
    kwargs = engine_kwargs()
    assert kwargs["pool_pre_ping"] is True
    assert kwargs["pool_recycle"] == 2700 and kwargs["pool_recycle"] < TOKEN_LIFE_SECONDS
    assert kwargs["connect_args"]["timeout"] == 10


@pytest.mark.parametrize("value", ["false", "False", "0", "no"])
def test_pre_ping_can_be_turned_off(engine_kwargs, monkeypatch, value):
    monkeypatch.setenv("DB_POOL_PRE_PING", value)
    assert engine_kwargs()["pool_pre_ping"] is False


def test_env_overrides_recycle_and_connect_timeout(engine_kwargs, monkeypatch):
    monkeypatch.setenv("DB_POOL_RECYCLE_INTERVAL", "1800")
    monkeypatch.setenv("DB_CONNECT_TIMEOUT", "5")
    kwargs = engine_kwargs()
    assert kwargs["pool_recycle"] == 1800
    assert kwargs["connect_args"]["timeout"] == 5


def test_app_yaml_keeps_safe_pool_settings():
    """app.yaml values win over the code defaults when deployed, so they must be safe too."""
    env = {e["name"]: e.get("value") for e in yaml.safe_load((FASTAPI_DIR / "app.yaml").read_text())["env"]}
    assert int(env["DB_POOL_RECYCLE_INTERVAL"]) < TOKEN_LIFE_SECONDS
    assert env.get("DB_POOL_PRE_PING", "true").lower() in ("1", "true", "yes")
