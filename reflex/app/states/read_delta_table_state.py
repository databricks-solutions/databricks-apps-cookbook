import reflex as rx
from typing import Any
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import logging
import pandas as pd

_connection = None


def get_connection(http_path: str):
    global _connection
    if _connection:
        return _connection
    cfg = Config()
    connection = sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )
    _connection = connection
    return connection


def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()


def pandas_to_editor_format(
    df: pd.DataFrame,
) -> tuple[list[list[str | int | float | bool | None]], list[dict[str, str]]]:
    """Convert a pandas DataFrame to the format required by rx.data_editor."""
    if df.empty:
        return ([], [])
    columns = []
    df_processed = df.copy()
    for col in df.columns:
        dtype = df[col].dtype
        col_type = "str"
        if pd.api.types.is_integer_dtype(dtype):
            col_type = "int"
            df_processed[col] = df_processed[col].fillna(0)
        elif pd.api.types.is_float_dtype(dtype):
            col_type = "float"
            df_processed[col] = df_processed[col].fillna(0.0)
        elif pd.api.types.is_bool_dtype(dtype):
            col_type = "bool"
            df_processed[col] = df_processed[col].fillna(False)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_type = "str"
            df_processed[col] = df_processed[col].astype(str).replace("NaT", "")
        else:
            col_type = "str"
            df_processed[col] = df_processed[col].fillna("").astype(str)
        columns.append({"title": col, "id": col, "type": col_type})
    data = df_processed.values.tolist()
    return (data, columns)


class ReadTableState(rx.State):
    warehouse_paths: dict[str, str] = {}
    catalogs: list[str] = []
    schema_names: list[str] = []
    table_names: list[str] = []
    selected_warehouse: str = ""
    selected_catalog: str = ""
    selected_schema: str = ""
    selected_table: str = ""
    df_data: list[list[str | int | float | bool | None]] = []
    df_columns: list[dict] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def columns_for_editor(self) -> list[dict]:
        return self.df_columns

    @rx.var
    def data_for_editor(self) -> list[list[str | int | float | bool | None]]:
        """Return data directly as it is already formatted for the editor."""
        return self.df_data

    @rx.var
    def warehouse_names(self) -> list[str]:
        return list(self.warehouse_paths.keys())

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
            logging.exception(f"Error initializing data: {e}")
            async with self:
                self.error_message = f"Error initializing data: {e}"
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
            self.df_data = []
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
            self.df_data = []
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

    @rx.event(background=True)
    async def set_selected_table(self, value: str):
        async with self:
            self.selected_table = value
            if value:
                self.is_loading = True
        if value:
            return ReadTableState.load_table

    @rx.event(background=True)
    async def load_table(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.df_data = []
            self.df_columns = []
            if not self.selected_warehouse:
                self.error_message = "Please select a Warehouse."
                self.is_loading = False
                return
            if (
                not self.selected_catalog
                or not self.selected_schema
                or (not self.selected_table)
            ):
                self.error_message = "Please select Catalog, Schema, and Table."
                self.is_loading = False
                return
            http_path = self.warehouse_paths.get(self.selected_warehouse)
            full_table_name = (
                f"{self.selected_catalog}.{self.selected_schema}.{self.selected_table}"
            )
        try:
            conn = get_connection(http_path)
            df = read_table(full_table_name, conn)
            data, cols = pandas_to_editor_format(df)
            async with self:
                self.df_data = data
                self.df_columns = cols
        except Exception as e:
            logging.exception(f"Error loading Delta table: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False