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
            run = w.jobs.get_run(run_id=run_id_int)
            agg_sql = []
            agg_dbt = []
            agg_job = []
            agg_nb = []

            def _collect(output_resp, name):
                d = output_resp.as_dict()
                if "sql_output" in d:
                    agg_sql.append({"task": name, "output": d["sql_output"]})
                if "dbt_output" in d:
                    agg_dbt.append({"task": name, "output": d["dbt_output"]})
                if "run_job_output" in d:
                    agg_job.append({"task": name, "output": d["run_job_output"]})
                if "notebook_output" in d:
                    agg_nb.append({"task": name, "output": d["notebook_output"]})

            if run.tasks:
                for task in run.tasks:
                    if task.run_id:
                        t_out = w.jobs.get_run_output(run_id=task.run_id)
                        _collect(t_out, task.task_key or f"Task {task.run_id}")
            else:
                run_output = w.jobs.get_run_output(run_id=run_id_int)
                _collect(run_output, "Main Run")
            async with self:
                if agg_sql:
                    self.sql_output = json.dumps(agg_sql, indent=2)
                if agg_dbt:
                    self.dbt_output = json.dumps(agg_dbt, indent=2)
                if agg_job:
                    self.run_job_output = json.dumps(agg_job, indent=2)
                if agg_nb:
                    self.notebook_output = json.dumps(agg_nb, indent=2)
                yield rx.toast("Results retrieved successfully.", level="success")
        except Exception as e:
            logging.exception(f"Error retrieving job results: {e}")
            async with self:
                self.error_message = f"Error: {e}"
                yield rx.toast(f"Error retrieving job results: {e}", level="error")
        finally:
            async with self:
                self.is_loading = False