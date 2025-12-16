import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.connect_cluster_state import ConnectClusterState
from app import theme

CODE_SNIPPET = """
import reflex as rx
import os
import asyncio
from typing import Any
from databricks.connect import DatabricksSession
import pandas as pd

def run_spark_workload(host: str, cluster_id: str):
    spark = DatabricksSession.builder.remote(
        host=host,
        cluster_id=cluster_id
    ).getOrCreate()

    session_info = {
        "App Name": spark.conf.get("spark.app.name", "Unknown"),
        "Master URL": spark.conf.get("spark.master", "Unknown"),
    }

    query = "SELECT 'I''m a stellar cook!' AS message"
    df_sql = spark.sql(query).toPandas()

    df_range = spark.range(10).toPandas()

    return session_info, df_sql.values.tolist(), df_range.values.tolist()

class ConnectClusterState(rx.State):
    cluster_id: str = ""
    session_info: dict = {}
    sql_output: list[list[Any]] = []
    range_output: list[list[Any]] = []
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""

    @rx.event(background=True)
    async def connect_and_run(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.success_message = ""
        try:
            host = os.getenv("DATABRICKS_HOST")
            loop = asyncio.get_running_loop()
            info, sql_res, range_res = await loop.run_in_executor(
                None, run_spark_workload, host, self.cluster_id
            )
            async with self:
                self.session_info = info
                self.sql_output = sql_res
                self.range_output = range_res
                self.success_message = "Successfully connected to Spark"
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
"""


def connect_cluster_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                "* `CAN ATTACH TO` permission on the cluster",
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
            rx.markdown("* All-purpose compute", class_name="text-sm text-gray-600"),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* `databricks-connect`
* `reflex`
""",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def connect_cluster_content() -> rx.Component:
    """Content for the 'Try It' tab of the Connect to Cluster page."""
    return rx.vstack(
        rx.vstack(
            rx.text("Specify cluster id:", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="0709-132523-cnhxf2p6",
                on_change=ConnectClusterState.set_cluster_id,
                class_name="w-full",
                default_value=ConnectClusterState.cluster_id,
            ),
            rx.text(
                "Copy a shared Compute cluster ID to connect to.",
                class_name="text-xs text-gray-500",
            ),
            width="100%",
        ),
        rx.button(
            "Connect and Run",
            on_click=ConnectClusterState.connect_and_run,
            is_loading=ConnectClusterState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
        ),
        rx.cond(
            ConnectClusterState.success_message,
            rx.box(
                rx.hstack(
                    rx.icon("circle_check", class_name="text-green-500 mr-2"),
                    rx.text(ConnectClusterState.success_message, color="green.700"),
                ),
                class_name="p-4 bg-green-50 border border-green-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            ConnectClusterState.error_message,
            rx.box(
                rx.hstack(
                    rx.icon("triangle-alert", class_name="text-red-500 mr-2"),
                    rx.text(ConnectClusterState.error_message, color="red.500"),
                ),
                class_name="p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            ConnectClusterState.session_info,
            rx.vstack(
                rx.text("Session Info", class_name="font-semibold text-sm mt-2"),
                rx.code_block(
                    ConnectClusterState.session_info.to_string(),
                    language="json",
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            ConnectClusterState.sql_output,
            rx.vstack(
                rx.text(
                    "SQL Output (SELECT 'I''m a stellar cook!' AS message)",
                    class_name="font-semibold text-sm mt-2",
                ),
                rx.data_editor(
                    data=ConnectClusterState.sql_output,
                    columns=[{"title": "message", "type": "str", "id": "message"}],
                    is_readonly=True,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            ConnectClusterState.range_output,
            rx.vstack(
                rx.text(
                    "Range Output (spark.range(10))",
                    class_name="font-semibold text-sm mt-2",
                ),
                rx.data_editor(
                    data=ConnectClusterState.range_output,
                    columns=[{"title": "id", "type": "int", "id": "id"}],
                    is_readonly=True,
                    class_name="w-full",
                ),
                width="100%",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def connect_cluster_page() -> rx.Component:
    """The Connect to a Cluster sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Connect to a Databricks Cluster",
            page_description="Connect to a Databricks cluster using Databricks Connect and execute Spark commands.",
            try_it_content=connect_cluster_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=connect_cluster_requirements,
        )
    )