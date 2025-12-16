import reflex as rx
from databricks.sdk import WorkspaceClient
import logging
import json


class RetrieveJobResultsState(rx.State):
    """State for Retrieve Job Results page."""

    task_run_id: str = ""
    sql_output: str = ""
    dbt_output: str = ""
    run_job_output: str = ""
    notebook_output: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    def set_task_run_id(self, value: str):
        self.task_run_id = value

    @rx.event(background=True)
    async def get_results(self):
        async with self:
            self.error_message = ""
            self.sql_output = ""
            self.dbt_output = ""
            self.run_job_output = ""
            self.notebook_output = ""
            if not self.task_run_id:
                yield rx.toast("Please specify a Task Run ID.", level="warning")
                return
            self.is_loading = True
        yield
        try:
            w = WorkspaceClient()
            try:
                run_id_int = int(self.task_run_id)
            except ValueError as e:
                logging.exception(f"Invalid Task Run ID: {e}")
                async with self:
                    self.error_message = "Task Run ID must be a valid number."
                    yield rx.toast("Task Run ID must be a valid number.", level="error")
                return
            run_output = w.jobs.get_run_output(run_id=run_id_int)
            output_dict = run_output.as_dict()
            async with self:
                if "sql_output" in output_dict:
                    self.sql_output = json.dumps(output_dict["sql_output"], indent=2)
                if "dbt_output" in output_dict:
                    self.dbt_output = json.dumps(output_dict["dbt_output"], indent=2)
                if "run_job_output" in output_dict:
                    self.run_job_output = json.dumps(
                        output_dict["run_job_output"], indent=2
                    )
                if "notebook_output" in output_dict:
                    self.notebook_output = json.dumps(
                        output_dict["notebook_output"], indent=2
                    )
                yield rx.toast("Results retrieved successfully.", level="success")
        except Exception as e:
            logging.exception(f"Error retrieving job results: {e}")
            async with self:
                self.error_message = f"Error: {e}"
                yield rx.toast(f"Error retrieving job results: {e}", level="error")
        finally:
            async with self:
                self.is_loading = False