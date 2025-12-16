import reflex as rx
import psycopg
from psycopg_pool import ConnectionPool
from databricks.sdk import WorkspaceClient
import pandas as pd
import uuid
import datetime
import logging
from typing import Union

_pool: ConnectionPool | None = None


class RotatingTokenConnection(psycopg.Connection):
    def __init__(self, *args, **kwargs):
        self._instance_name = kwargs.pop("_instance_name")
        super().__init__(*args, **kwargs)

    @classmethod
    def connect(cls, *args, **kwargs):
        if "_instance_name" in kwargs:
            instance_name = kwargs["_instance_name"]
            w = WorkspaceClient()
            credential = w.database.generate_database_credential(
                request_id=str(uuid.uuid4()), instance_names=[instance_name]
            )
            kwargs["password"] = credential.token
        return super().connect(*args, **kwargs)


def build_pool(instance_name: str, host: str, user: str, database: str):
    return ConnectionPool(
        conninfo=f"host={host} dbname={database} user={user} sslmode=require",
        min_size=1,
        max_size=5,
        open=True,
        kwargs={"_instance_name": instance_name},
        connection_class=RotatingTokenConnection,
    )


def query_df(query: str, params=None) -> pd.DataFrame:
    global _pool
    if _pool is None:
        raise ConnectionError("Connection pool is not initialized.")
    with _pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description is None:
                return pd.DataFrame()
            cols = [desc[0] for desc in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=cols)


def upsert_app_state(schema: str, table: str, session_id: str, key: str, value: str):
    create_sql = f"\n    CREATE TABLE IF NOT EXISTS {schema}.{table} (\n        session_id TEXT,\n        key TEXT,\n        value TEXT,\n        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n        PRIMARY KEY (session_id, key)\n    );\n    "
    query_df(create_sql)
    upsert_sql = f"\n    INSERT INTO {schema}.{table} (session_id, key, value, updated_at) \n    VALUES (%(session_id)s, %(key)s, %(value)s, CURRENT_TIMESTAMP)\n    ON CONFLICT (session_id, key) DO UPDATE SET\n        value = EXCLUDED.value,\n        updated_at = EXCLUDED.updated_at;\n    "
    query_df(upsert_sql, params={"session_id": session_id, "key": key, "value": value})


class OltpDatabaseState(rx.State):
    session_id: str = str(uuid.uuid4())
    instance_names: list[str] = []
    selected_instance: str = ""
    database: str = "databricks_postgres"
    schema_name: str = "public"
    table_name: str = "app_state"
    result_data: list[
        dict[str, Union[str, int, float, bool, None, datetime.datetime]]
    ] = []
    result_columns: list[str] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def result_columns_for_editor(self) -> list[dict[str, str]]:
        """Format columns for the data editor."""
        return [{"title": col, "id": col} for col in self.result_columns]

    @rx.var
    def result_data_for_editor(
        self,
    ) -> list[list[Union[str, int, float, bool, None, datetime.datetime]]]:
        """Format data for the data editor."""
        if not self.result_data or not self.result_columns:
            return []
        return [
            [row.get(col) for col in self.result_columns] for row in self.result_data
        ]

    @rx.event(background=True)
    async def load_instances(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.instance_names = []
        try:
            w = WorkspaceClient()
            instances = w.database.list_database_instances()
            async with self:
                self.instance_names = [i.name for i in instances]
                if self.instance_names:
                    self.selected_instance = self.instance_names[0]
        except Exception as e:
            logging.exception(f"Failed to load database instances: {e}")
            async with self:
                self.error_message = f"Failed to load database instances: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def run_query(self):
        global _pool
        async with self:
            if not self.selected_instance:
                self.error_message = "Please select a database instance first."
                return
            self.is_loading = True
            self.error_message = ""
            self.result_data = []
            self.result_columns = []
        try:
            w = WorkspaceClient()
            if _pool is None:
                user = w.current_user.me().user_name
                instance = w.database.get_database_instance(name=self.selected_instance)
                host = instance.read_write_dns
                _pool = build_pool(
                    instance_name=self.selected_instance,
                    host=host,
                    user=user,
                    database=self.database,
                )
            upsert_app_state(
                self.schema_name,
                self.table_name,
                self.session_id,
                "feedback_message",
                "true",
            )
            select_sql = f"SELECT * FROM {self.schema_name}.{self.table_name} WHERE session_id = %(session_id)s"
            df = query_df(select_sql, params={"session_id": self.session_id})
            async with self:
                self.result_data = df.to_dict("records")
                self.result_columns = df.columns.to_list()
        except Exception as e:
            logging.exception(f"An error occurred during query execution: {e}")
            async with self:
                self.error_message = f"An error occurred: {e}"
        finally:
            async with self:
                self.is_loading = False