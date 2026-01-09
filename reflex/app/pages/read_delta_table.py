import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.components.loading_spinner import loading_spinner
from app.states.read_delta_table_state import ReadTableState
from app import theme

CODE_SNIPPET = '''import reflex as rx
from databricks import sql
from databricks.sdk.core import Config
import logging
import pandas as pd
from typing import Any

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
            # Default value below
            df_processed[col] = df_processed[col].fillna(0)
        elif pd.api.types.is_float_dtype(dtype):
            col_type = "float"
            # Default value below
            df_processed[col] = df_processed[col].fillna(0.0)
        elif pd.api.types.is_bool_dtype(dtype):
            col_type = "bool"
            # Default value below
            df_processed[col] = df_processed[col].fillna(False)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col_type = "str"
            # Default value below
            df_processed[col] = df_processed[col].astype(str).replace("NaT", "")
        else:
            col_type = "str"
            # Default value below
            df_processed[col] = df_processed[col].fillna("").astype(str)
        columns.append({"title": col, "id": col, "type": col_type})
    data = df_processed.values.tolist()
    return (data, columns)


class ReadTableState(rx.State):
    http_path_input: str = ""
    table_name: str = "samples.nyctaxi.trips"
    df_data: list[list[Any]] = []
    df_columns: list[dict] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def columns_for_editor(self) -> list[dict]:
        return self.df_columns

    @rx.var
    def data_for_editor(self) -> list[list[str]]:
        """Return data directly as it is already formatted for the editor."""
        return self.df_data

    @rx.event(background=True)
    async def load_table(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.df_data = []
            self.df_columns = []
            http_path = self.http_path_input
            table_name = self.table_name
        if not http_path:
            async with self:
                self.error_message = "Please enter an HTTP Path."
                self.is_loading = False
            return
        try:
            conn = get_connection(http_path)
            df = read_table(table_name, conn)
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
'''


def read_delta_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
The app service principal requires:
* `CAN USE` on the SQL Warehouse
* `SELECT` on the Unity Catalog table
""",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Databricks resources",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
You need:
* A running SQL Warehouse
* A populated Delta table in Unity Catalog
""",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.el.ul(
                rx.el.li(
                    rx.link(
                        "databricks-sdk",
                        href="https://pypi.org/project/databricks-sdk/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                rx.el.li(
                    rx.link(
                        "databricks-sql-connector",
                        href="https://pypi.org/project/databricks-sql-connector/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                rx.el.li(
                    rx.link(
                        "reflex",
                        href="https://pypi.org/project/reflex/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                rx.el.li(
                    rx.link(
                        "pandas",
                        href="https://pypi.org/project/pandas/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                class_name="list-disc list-inside text-sm text-gray-600 pl-2",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def read_delta_content() -> rx.Component:
    """Content for the 'Try It' tab of the Read Delta Table page."""
    return rx.vstack(
        rx.vstack(
            rx.text("Select a Warehouse", class_name="font-semibold text-sm"),
            rx.select(
                ReadTableState.warehouse_names,
                placeholder="Select SQL Warehouse...",
                on_change=ReadTableState.set_selected_warehouse,
                value=ReadTableState.selected_warehouse,
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Select a Catalog", class_name="font-semibold text-sm"),
            rx.select(
                ReadTableState.catalogs,
                placeholder="Select Catalog...",
                on_change=ReadTableState.set_selected_catalog,
                value=ReadTableState.selected_catalog,
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.cond(
            ReadTableState.selected_catalog,
            rx.vstack(
                rx.text("Select a Schema", class_name="font-semibold text-sm"),
                rx.select(
                    ReadTableState.schema_names,
                    placeholder="Select Schema...",
                    on_change=ReadTableState.set_selected_schema,
                    value=ReadTableState.selected_schema,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            ReadTableState.selected_schema,
            rx.vstack(
                rx.text("Select a Table", class_name="font-semibold text-sm"),
                rx.select(
                    ReadTableState.table_names,
                    placeholder="Select Table...",
                    on_change=ReadTableState.set_selected_table,
                    value=ReadTableState.selected_table,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            ReadTableState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(ReadTableState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            ReadTableState.is_loading,
            loading_spinner("Loading table data..."),
            rx.cond(
                ReadTableState.df_data,
                rx.data_editor(
                    columns=ReadTableState.columns_for_editor,
                    data=ReadTableState.data_for_editor,
                    is_readonly=True,
                    height="60vh",
                    width="95%",
                    class_name="overflow-auto",
                ),
            ),
        ),
        spacing="4",
        align="start",
        class_name="w-full",
    )


def read_delta_table_page() -> rx.Component:
    """The Read a Delta table sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Read a Delta Table",
            page_description="Securely connect to your Databricks environment and read data from a Delta table into your Reflex application.",
            try_it_content=read_delta_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=read_delta_requirements,
        )
    )