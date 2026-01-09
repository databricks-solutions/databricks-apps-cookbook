import reflex as rx
from typing import Any
import pandas as pd
import logging
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config


class OnBehalfOfUserState(rx.State):
    warehouse_paths: dict[str, str] = {}
    catalogs: list[str] = []
    schema_names: list[str] = []
    table_names: list[str] = []
    selected_warehouse: str = ""
    selected_catalog: str = ""
    selected_schema: str = ""
    selected_table: str = ""
    auth_mode: str = "On-behalf-of-user (OBO)"
    data: list[list[str | int | float | bool | None]] = []
    columns: list[dict[str, str]] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def warehouse_names(self) -> list[str]:
        return list(self.warehouse_paths.keys())

    @rx.var
    def columns_for_editor(self) -> list[dict]:
        return self.columns

    @rx.var
    def data_for_editor(self) -> list[list[str | int | float | bool | None]]:
        return self.data

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            w = WorkspaceClient()
            warehouses = w.warehouses.list()
            warehouse_map = {wh.name: wh.odbc_params.path for wh in warehouses}
            catalogs = w.catalogs.list()
            catalog_list = [c.name for c in catalogs]
            async with self:
                self.warehouse_paths = warehouse_map
                self.catalogs = catalog_list
        except Exception as e:
            logging.exception(f"Error loading metadata: {e}")
            async with self:
                self.error_message = f"Error loading metadata: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_selected_warehouse(self, value: str):
        self.selected_warehouse = value

    @rx.event(background=True)
    async def set_selected_catalog(self, value: str):
        async with self:
            self.selected_catalog = value
            self.selected_schema = ""
            self.selected_table = ""
            self.schema_names = []
            self.table_names = []
            self.is_loading = True
        try:
            w = WorkspaceClient()
            schemas = w.schemas.list(catalog_name=value)
            async with self:
                self.schema_names = [s.name for s in schemas]
        except Exception as e:
            logging.exception(f"Error fetching schemas: {e}")
            async with self:
                self.error_message = f"Error fetching schemas: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def set_selected_schema(self, value: str):
        async with self:
            self.selected_schema = value
            self.selected_table = ""
            self.table_names = []
            self.is_loading = True
        try:
            w = WorkspaceClient()
            tables = w.tables.list(
                catalog_name=self.selected_catalog, schema_name=value
            )
            async with self:
                self.table_names = [t.name for t in tables]
        except Exception as e:
            logging.exception(f"Error fetching tables: {e}")
            async with self:
                self.error_message = f"Error fetching tables: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_selected_table(self, value: str):
        self.selected_table = value

    @rx.event
    def set_auth_mode(self, value: str):
        self.auth_mode = value

    @rx.event(background=True)
    async def run_query(self):
        async with self:
            if (
                not self.selected_warehouse
                or not self.selected_catalog
                or (not self.selected_schema)
                or (not self.selected_table)
            ):
                self.error_message = "Please select all fields."
                return
            self.is_loading = True
            self.error_message = ""
            self.data = []
            self.columns = []
            http_path = self.warehouse_paths.get(self.selected_warehouse)
            full_table_name = (
                f"{self.selected_catalog}.{self.selected_schema}.{self.selected_table}"
            )
            token = ""
            if self.auth_mode == "On-behalf-of-user (OBO)":
                headers = self.router.headers
                token = getattr(headers, "x_forwarded_access_token", "")
                if not token:
                    self.error_message = (
                        "No OBO token found. Are you running in Databricks Apps?"
                    )
                    self.is_loading = False
                    return
        try:
            cfg = Config()
            connection = None
            if self.auth_mode == "On-behalf-of-user (OBO)":
                connection = sql.connect(
                    server_hostname=cfg.host, http_path=http_path, access_token=token
                )
            else:
                connection = sql.connect(
                    server_hostname=cfg.host,
                    http_path=http_path,
                    credentials_provider=cfg.authenticate,
                )
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {full_table_name} LIMIT 100")
                df = cursor.fetchall_arrow().to_pandas()
            data = df.values.tolist()
            cols = [{"title": col, "id": col, "type": "str"} for col in df.columns]
            async with self:
                self.data = data
                self.columns = cols
                if self.auth_mode == "On-behalf-of-user (OBO)":
                    yield rx.toast(
                        "Query executed successfully as user.", level="success"
                    )
                else:
                    yield rx.toast(
                        "Query executed successfully as service principal.",
                        level="success",
                    )
        except Exception as e:
            logging.exception(f"Error executing query: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False