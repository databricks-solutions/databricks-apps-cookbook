import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.states.on_behalf_of_user_state import OnBehalfOfUserState
from app import theme

CODE_SNIPPET = """
import reflex as rx
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

_connection = None

def get_user_token(headers):
    return getattr(headers, "x_forwarded_access_token", "")

def connect_with_obo(http_path: str, user_token: str):
    global _connection
    if _connection:
        return _connection
    _connection = sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        access_token=user_token
    )
    return _connection

def execute_query(table_name: str, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name} LIMIT 10"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

class OboState(rx.State):
    warehouse_paths: dict[str, str] = {}
    selected_warehouse: str = ""
    table_name: str = "samples.nyctaxi.trips"
    data: list[list] = []
    columns: list[dict] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def run_query(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            headers = self.router.headers
            user_token = get_user_token(headers)

        if not user_token:
            async with self:
                self.error_message = "No OBO token found."
                self.is_loading = False
            return

        try:
            http_path = self.warehouse_paths.get(self.selected_warehouse)
            conn = connect_with_obo(http_path, user_token)
            df = execute_query(self.table_name, conn)

            # Process dataframe for display
            d = df.values.tolist()
            c = [{"title": col, "id": col, "type": "str"} for col in df.columns]

            async with self:
                self.data = d
                self.columns = c
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
"""


def on_behalf_of_user_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* `SELECT` on the Unity Catalog table
* `CAN USE` on the SQL Warehouse

(Applies to the user in OBO mode, or the app service principal in SP mode)
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
* SQL Warehouse
* Unity Catalog table
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
                class_name="list-disc list-inside text-sm text-gray-600 pl-2",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def on_behalf_of_user_content() -> rx.Component:
    """Content for the 'Try It' tab."""
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.icon("info", class_name="h-5 w-5 text-blue-600"),
                rx.text(
                    "Enable on-behalf-of-user authentication (OBO) for this app to execute queries using the visiting user's identity. The Service Principal mode uses the app's own identity.",
                    class_name="text-sm text-blue-800",
                ),
                align="center",
                spacing="2",
            ),
            class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg w-full mb-4",
        ),
        rx.vstack(
            rx.text("Select a Warehouse", class_name="font-semibold text-sm"),
            rx.select(
                OnBehalfOfUserState.warehouse_names,
                placeholder="Select SQL Warehouse...",
                on_change=OnBehalfOfUserState.set_selected_warehouse,
                value=OnBehalfOfUserState.selected_warehouse,
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Select a Catalog", class_name="font-semibold text-sm"),
            rx.select(
                OnBehalfOfUserState.catalogs,
                placeholder="Select Catalog...",
                on_change=OnBehalfOfUserState.set_selected_catalog,
                value=OnBehalfOfUserState.selected_catalog,
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.cond(
            OnBehalfOfUserState.selected_catalog,
            rx.vstack(
                rx.text("Select a Schema", class_name="font-semibold text-sm"),
                rx.select(
                    OnBehalfOfUserState.schema_names,
                    placeholder="Select Schema...",
                    on_change=OnBehalfOfUserState.set_selected_schema,
                    value=OnBehalfOfUserState.selected_schema,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            OnBehalfOfUserState.selected_schema,
            rx.vstack(
                rx.text("Select a Table", class_name="font-semibold text-sm"),
                rx.select(
                    OnBehalfOfUserState.table_names,
                    placeholder="Select Table...",
                    on_change=OnBehalfOfUserState.set_selected_table,
                    value=OnBehalfOfUserState.selected_table,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.vstack(
            rx.text("Authentication Mode", class_name="font-semibold text-sm"),
            rx.select(
                ["On-behalf-of-user (OBO)", "Service principal"],
                value=OnBehalfOfUserState.auth_mode,
                on_change=OnBehalfOfUserState.set_auth_mode,
                width="100%",
            ),
            width="100%",
        ),
        rx.button(
            "Run Query (Limit 100)",
            on_click=OnBehalfOfUserState.run_query,
            is_loading=OnBehalfOfUserState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            OnBehalfOfUserState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(OnBehalfOfUserState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            OnBehalfOfUserState.is_loading,
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Running query...", class_name="text-gray-500"),
                align="center",
                justify="center",
                class_name="w-full h-48 bg-gray-50 rounded-lg",
            ),
            rx.cond(
                OnBehalfOfUserState.data,
                rx.data_editor(
                    columns=OnBehalfOfUserState.columns_for_editor,
                    data=OnBehalfOfUserState.data_for_editor,
                    is_readonly=True,
                    class_name="w-full h-96",
                ),
            ),
        ),
        spacing="4",
        align="start",
        width="100%",
    )


def on_behalf_of_user_page() -> rx.Component:
    """The On-Behalf-Of-User sample page."""
    return rx.fragment(
        main_layout(
            tabbed_page_template(
                page_title="On-Behalf-Of User Authentication",
                page_description="Implement the OAuth on-behalf-of flow where the app performs actions as the end-user using their token.",
                try_it_content=on_behalf_of_user_content,
                code_snippet_content=CODE_SNIPPET,
                requirements_content=on_behalf_of_user_requirements,
            )
        ),
        on_mount=OnBehalfOfUserState.on_load,
    )