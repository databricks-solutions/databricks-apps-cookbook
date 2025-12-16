import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.states.edit_delta_table_state import EditDeltaTableState
from app import theme

CODE_SNIPPET = """
import reflex as rx
from typing import Any
import pandas as pd
import datetime
from databricks import sql
from databricks.sdk.core import Config

_connection = None

def get_connection(http_path: str):
    global _connection
    if _connection:
        return _connection
    cfg = Config()
    connection = sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=cfg.authenticate,
    )
    _connection = connection
    return connection

def insert_overwrite_table(table_name: str, df: pd.DataFrame, connection):
    if df.empty:
        # If the dataframe is empty, we skip the overwrite to avoid
        # accidentally truncating the table if the UI state was not fully loaded.
        return

    def format_val(x):
        if x is None or pd.isna(x):
            return "NULL"
        if isinstance(x, str):
            return f"'{x.replace("'", "''")}'"
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
    # Key state fields for managing selection and data
    warehouse_paths: dict[str, str] = {}
    selected_warehouse: str = ""
    selected_catalog: str = ""
    selected_schema: str = ""
    selected_table: str = ""

    # Data for the editor
    columns: list[dict[str, str]] = []
    table_data: list[list[Any]] = []
    original_table_data: list[list[Any]] = []

    is_saving: bool = False

    @rx.event
    def handle_cell_change(
        self, new_value: Any, row_index: int, col_index: int
    ):
        "Update table data when a cell is edited."
        if row_index < len(self.table_data):
            row = self.table_data[row_index]
            if col_index < len(row):
                self.table_data[row_index][col_index] = new_value

    @rx.event
    async def save_changes(self):
        self.is_saving = True
        yield
        try:
            col_names = [col["title"] for col in self.columns]
            df = pd.DataFrame(self.table_data, columns=col_names)

            http_path = self.warehouse_paths.get(self.selected_warehouse)
            full_table_name = f"{self.selected_catalog}.{self.selected_schema}.{self.selected_table}"
            conn = get_connection(http_path)

            insert_overwrite_table(full_table_name, df, conn)

            self.original_table_data = [row[:] for row in self.table_data]
            yield rx.toast(f"Successfully saved changes to {full_table_name}.")
        except Exception as e:
            yield rx.toast(f"Error saving changes: {e}", level="error")
        finally:
            self.is_saving = False
"""


def edit_delta_requirements() -> rx.Component:
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
* `MODIFY` on the Unity Catalog table
* `CAN USE` on the SQL Warehouse
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
            rx.text("You need:", class_name="text-sm text-gray-600"),
            rx.el.ul(
                rx.el.li("A running SQL Warehouse"),
                rx.el.li("A populated Delta table in Unity Catalog"),
                class_name="list-disc list-inside text-sm text-gray-600 pl-2",
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
                        "pandas",
                        href="https://pypi.org/project/pandas/",
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
                class_name="list-disc list-inside text-sm text-gray-600 pl-2",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def editable_table_component() -> rx.Component:
    """The UI for the editable table and its controls."""
    return rx.vstack(
        rx.vstack(
            rx.text("Select a Warehouse", class_name="font-semibold text-sm"),
            rx.select(
                EditDeltaTableState.warehouse_names,
                placeholder="Select SQL Warehouse...",
                on_change=EditDeltaTableState.set_selected_warehouse,
                value=EditDeltaTableState.selected_warehouse,
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Select a Catalog", class_name="font-semibold text-sm"),
            rx.select(
                EditDeltaTableState.catalogs,
                placeholder="Select Catalog...",
                on_change=EditDeltaTableState.set_selected_catalog,
                value=EditDeltaTableState.selected_catalog,
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.cond(
            EditDeltaTableState.selected_catalog,
            rx.vstack(
                rx.text("Select a Schema", class_name="font-semibold text-sm"),
                rx.select(
                    EditDeltaTableState.schema_names,
                    placeholder="Select Schema...",
                    on_change=EditDeltaTableState.set_selected_schema,
                    value=EditDeltaTableState.selected_schema,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            EditDeltaTableState.selected_schema,
            rx.vstack(
                rx.text("Select a Table", class_name="font-semibold text-sm"),
                rx.select(
                    EditDeltaTableState.table_names,
                    placeholder="Select Table...",
                    on_change=EditDeltaTableState.set_selected_table,
                    value=EditDeltaTableState.selected_table,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            EditDeltaTableState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(EditDeltaTableState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full mb-4",
            ),
        ),
        rx.cond(
            EditDeltaTableState.is_loading,
            rx.vstack(
                rx.spinner(size="3", class_name="mb-2"),
                rx.text("Loading Table Data...", class_name="text-gray-500"),
                align="center",
                justify="center",
                class_name="w-full h-64 bg-gray-50 rounded-lg",
            ),
        ),
        rx.cond(
            EditDeltaTableState.selected_table
            & ~EditDeltaTableState.is_loading
            & EditDeltaTableState.table_data,
            rx.vstack(
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.foreach(
                                    EditDeltaTableState.columns,
                                    lambda col: rx.el.th(
                                        col["title"],
                                        class_name="px-4 py-2 text-left text-sm font-semibold text-gray-700 bg-gray-50",
                                    ),
                                ),
                                class_name="border-b",
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                EditDeltaTableState.table_data,
                                lambda row, row_index: rx.el.tr(
                                    rx.foreach(
                                        row,
                                        lambda val, col_index: rx.el.td(
                                            rx.el.input(
                                                default_value=val,
                                                on_change=lambda new_val: EditDeltaTableState.handle_cell_change(
                                                    new_val, row_index, col_index
                                                ),
                                                class_name="w-full p-2 border-none focus:ring-2 rounded-md bg-transparent",
                                            ),
                                            class_name="px-4 py-2 text-sm",
                                        ),
                                    ),
                                    class_name="border-b hover:bg-gray-50",
                                ),
                            )
                        ),
                        class_name="w-full table-auto",
                    ),
                    class_name="overflow-x-auto border rounded-lg",
                ),
                rx.hstack(
                    rx.button(
                        "Save Changes",
                        rx.icon(tag="save", class_name="mr-2 h-4 w-4"),
                        on_click=EditDeltaTableState.save_changes,
                        is_loading=EditDeltaTableState.is_saving,
                        disabled=~EditDeltaTableState.has_changes,
                        class_name="mt-4 text-white px-4 py-2 rounded-lg disabled:opacity-50 hover:opacity-80",
                        bg=theme.PRIMARY_COLOR,
                    ),
                    justify="end",
                    class_name="w-full mt-4",
                ),
                align="start",
                class_name="w-full",
            ),
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def edit_delta_table_page() -> rx.Component:
    """The Edit a Delta table sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Edit a Delta Table",
            page_description="Select a table from your Databricks environment to view and edit its contents directly. Changes can be saved back to the Delta table.",
            try_it_content=editable_table_component,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=edit_delta_requirements,
        )
    )