import reflex as rx
import uuid
import pandas as pd
from databricks.sdk import WorkspaceClient
import psycopg
from psycopg_pool import ConnectionPool
from typing import Any
import asyncio
import logging

_pool = None


class RotatingTokenConnection(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        w = WorkspaceClient()
        instance_name = kwargs.pop("_instance_name", None)
        if instance_name:
            kwargs["password"] = w.database.generate_database_credential(
                request_id=str(uuid.uuid4()), instance_names=[instance_name]
            ).token
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)


def get_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=f"host={host} dbname={database} user={user}",
            connection_class=RotatingTokenConnection,
            kwargs={"_instance_name": instance_name},
            min_size=1,
            max_size=5,
            open=True,
        )
    return _pool


def query_df(pool: ConnectionPool, sql_query: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            if cur.description is None:
                return pd.DataFrame()
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


class OltpDatabaseState(rx.State):
    session_id: str = ""
    instance_name: str = ""
    instance_options: dict[str, str] = {}
    database: str = "databricks_postgres"
    schema_name: str = "public"
    table: str = "app_state"
    df_data: list[list[str | int | float | bool | None]] = []
    df_columns: list[dict[str, str]] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def instance_names(self) -> list[str]:
        return list(self.instance_options.keys())

    @rx.event
    def set_instance_name(self, value: str):
        self.instance_name = value

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            w = WorkspaceClient()
            instances = w.database.list_database_instances()
            options = {i.name: i.read_write_dns for i in instances}
            async with self:
                self.instance_options = options
                if options and (not self.instance_name):
                    self.instance_name = list(options.keys())[0]
        except Exception as e:
            logging.exception(f"Error fetching instances: {e}")
            async with self:
                self.error_message = f"Error fetching instances: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_database(self, value: str):
        self.database = value

    @rx.event
    def set_schema_name(self, value: str):
        self.schema_name = value

    @rx.event
    def set_table(self, value: str):
        self.table = value

    @rx.event(background=True)
    async def run_query(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            if not self.session_id:
                self.session_id = str(uuid.uuid4())
            if not self.instance_name:
                self.error_message = "Please select an instance."
                self.is_loading = False
                return
            current_instance = self.instance_name
            current_host = self.instance_options.get(current_instance)
            current_db = self.database
            current_schema = self.schema_name
            current_table = self.table
            current_session = self.session_id
        try:
            w = WorkspaceClient()

            def _execute_work():
                user = w.current_user.me().user_name
                host = current_host
                if not host:
                    host = w.database.get_database_instance(
                        name=current_instance
                    ).read_write_dns
                pool = get_pool(current_instance, host, user, current_db)
                with pool.connection() as conn:
                    with conn.cursor() as cur:
                        create_table_sql = f"\n                            CREATE TABLE IF NOT EXISTS {current_schema}.{current_table} (\n                                session_id TEXT,\n                                key TEXT,\n                                value TEXT,\n                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                                PRIMARY KEY (session_id, key)\n                            )\n                        "
                        cur.execute(create_table_sql)
                        upsert_sql = f"\n                            INSERT INTO {current_schema}.{current_table} (session_id, key, value, updated_at)\n                            VALUES ('{current_session}', 'feedback_message', 'true', CURRENT_TIMESTAMP)\n                            ON CONFLICT (session_id, key) DO UPDATE\n                            SET value = EXCLUDED.value,\n                                updated_at = CURRENT_TIMESTAMP\n                        "
                        cur.execute(upsert_sql)
                select_sql = f"SELECT * FROM {current_schema}.{current_table} WHERE session_id = '{current_session}'"
                return query_df(pool, select_sql)

            loop = asyncio.get_running_loop()
            df = await loop.run_in_executor(None, _execute_work)
            data = df.values.tolist()
            columns = [{"title": col, "id": col, "type": "str"} for col in df.columns]
            async with self:
                self.df_data = data
                self.df_columns = columns
        except Exception as e:
            logging.exception(f"Error executing query: {e}")
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False