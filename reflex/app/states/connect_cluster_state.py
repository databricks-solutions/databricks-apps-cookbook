import reflex as rx
import os
import asyncio
from typing import Any
import logging


def run_spark_workload(host: str, cluster_id: str):
    from databricks.connect import DatabricksSession

    spark = DatabricksSession.builder.remote(
        host=host, cluster_id=cluster_id
    ).getOrCreate()
    session_info = {
        "App Name": spark.conf.get("spark.app.name", "Unknown"),
        "Master URL": spark.conf.get("spark.master", "Unknown"),
    }
    query = "SELECT 'I''m a stellar cook!' AS message"
    df_sql = spark.sql(query).toPandas()
    df_range = spark.range(10).toPandas()
    return (session_info, df_sql.values.tolist(), df_range.values.tolist())


class ConnectClusterState(rx.State):
    """State for Connect Cluster page."""

    cluster_id: str = ""
    session_info: dict = {}
    sql_output: list[list[str | int | float | bool | None]] = []
    range_output: list[list[str | int | float | bool | None]] = []
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""

    @rx.event
    def set_cluster_id(self, value: str):
        self.cluster_id = value

    @rx.event(background=True)
    async def connect_and_run(self):
        async with self:
            if not self.cluster_id:
                self.error_message = "Please specify a Cluster ID."
                return
            self.is_loading = True
            self.error_message = ""
            self.success_message = ""
            self.session_info = {}
            self.sql_output = []
            self.range_output = []
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
            logging.exception(f"Error in connect_and_run: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False