import reflex as rx
from typing import Union, Any
import asyncio
import logging
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import pandas as pd
import datetime

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


def insert_overwrite_table(table_name: str, df: pd.DataFrame, connection):
    """
    Overwrites the Delta table with the provided DataFrame using INSERT OVERWRITE.
    Note: This method constructs a SQL string and is suitable for smaller tables
    typically used in these kinds of editable UI applications.
    """
    if df.empty:
        return

    def format_val(x):
        if x is None or pd.isna(x):
            return "NULL"
        if isinstance(x, str):
            return f"""'{x.replace("'", "''")}'"""
        if isinstance(x, (datetime.date, datetime.datetime, pd.Timestamp)):
            return f"'{x}'"
        return str(x)

    values = []
    for _, row in df.iterrows():
        row_values = [format_val(val) for val in row]
        values.append(f"({', '.join(row_values)})")
    sql_query = f"INSERT OVERWRITE TABLE {table_name} VALUES {', '.join(values)}"
    with connection.cursor() as cursor:
        cursor.execute(sql_query)


class EditDeltaTableState(rx.State):
    """State for the Edit a Delta table page."""

    warehouse_paths: dict[str, str] = {}
    catalogs: list[str] = []
    schema_names: list[str] = []
    table_names: list[str] = []
    selected_warehouse: str = ""
    selected_catalog: str = ""
    selected_schema: str = ""
    selected_table: str = ""
    columns: list[dict[str, str]] = []
    table_data: list[list[str | int | float | bool | None]] = []
    original_table_data: list[list[str | int | float | bool | None]] = []
    is_loading: bool = False
    is_saving: bool = False
    error_message: str = ""

    @rx.var
    def warehouse_names(self) -> list[str]:
        return list(self.warehouse_paths.keys())

    @rx.var
    def changes_summary(self) -> list[dict[str, Union[str, int, float, dict]]]:
        """Compares original and current data to find changes."""
        if not self.original_table_data or not self.table_data:
            return []
        changes = []
        for i, original_row in enumerate(self.original_table_data):
            if i < len(self.table_data):
                current_row = self.table_data[i]
                if original_row != current_row:
                    diff = {}
                    for col_idx, (orig_val, curr_val) in enumerate(
                        zip(original_row, current_row)
                    ):
                        if orig_val != curr_val:
                            col_title = (
                                self.columns[col_idx]["title"]
                                if col_idx < len(self.columns)
                                else str(col_idx)
                            )
                            diff[col_title] = (orig_val, curr_val)
                    if diff:
                        pk = original_row[0] if original_row else i
                        changes.append({"primary_key": pk, "changes": diff})
        return changes

    @rx.var
    def has_changes(self) -> bool:
        return len(self.changes_summary) > 0

    @rx.event(background=True)
    async def on_load(self):
        """Load warehouses on page load."""
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
            self.table_data = []
            self.columns = []
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
            self.table_data = []
            self.columns = []
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
            return EditDeltaTableState.load_table

    @rx.event(background=True)
    async def load_table(self):
        """Load data for the selected table."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.table_data = []
            self.columns = []
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
                self.table_data = data
                self.columns = cols
                self.original_table_data = [row[:] for row in self.table_data]
        except Exception as e:
            logging.exception(f"Error loading Delta table: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def handle_cell_change(self, pos: tuple[int, int], val: dict[str, Any]):
        """Update table data when a cell is edited."""
        col_index, row_index = pos
        if row_index < len(self.table_data):
            row = self.table_data[row_index]
            if col_index < len(row):
                self.table_data[row_index][col_index] = val["data"]

    @rx.event(background=True)
    async def save_changes(self):
        """Save changes to the Delta table."""
        async with self:
            self.is_saving = True
            current_table_data = self.table_data
            current_columns = self.columns
            warehouse = self.selected_warehouse
            catalog = self.selected_catalog
            schema = self.selected_schema
            table = self.selected_table
            http_path = self.warehouse_paths.get(warehouse)
        try:
            full_table_name = f"{catalog}.{schema}.{table}"
            col_names = [col["title"] for col in current_columns]
            df = pd.DataFrame(current_table_data, columns=col_names)
            conn = get_connection(http_path)
            insert_overwrite_table(full_table_name, df, conn)
            async with self:
                self.original_table_data = [row[:] for row in current_table_data]
            yield rx.toast(
                f"Successfully saved changes to {full_table_name}.", duration=3000
            )
        except Exception as e:
            logging.exception(f"Error saving changes: {e}")
            yield rx.toast(f"Error saving changes: {e}", level="error", duration=5000)
        finally:
            async with self:
                self.is_saving = False