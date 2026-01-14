import reflex as rx
import json
import logging
from databricks.sdk import WorkspaceClient


def trigger_workflow(job_id: str, params: dict) -> dict:
    """Helper function to trigger a Databricks Workflow job."""
    w = WorkspaceClient()
    try:
        run = w.jobs.run_now(job_id=int(job_id), job_parameters=params)
        return {"run_id": run.run_id, "state": "Triggered"}
    except Exception as e:
        logging.exception(f"Error triggering workflow: {e}")
        return {"error": str(e)}


class TriggerJobState(rx.State):
    """State for Trigger Job page."""

    job_id: str = ""
    parameters_input: str = ""
    result_data: str = ""
    error_message: str = ""
    is_loading: bool = False

    @rx.event
    def set_job_id(self, value: str):
        self.job_id = value

    @rx.event
    def set_parameters_input(self, value: str):
        self.parameters_input = value

    @rx.event(background=True)
    async def trigger_job(self):
        async with self:
            self.error_message = ""
            self.result_data = ""
            if not self.job_id:
                yield rx.toast("Please specify a Job ID.", level="warning")
                return
            self.is_loading = True
        yield
        try:
            try:
                if not self.parameters_input.strip():
                    params = {}
                else:
                    params = json.loads(self.parameters_input.strip())
            except json.JSONDecodeError as e:
                logging.exception(f"Invalid JSON parameters: {e}")
                async with self:
                    self.error_message = "Invalid JSON parameters."
                    yield rx.toast("Invalid JSON parameters.", level="error")
                return
            result = trigger_workflow(self.job_id, params)
            async with self:
                if "error" in result:
                    self.error_message = result["error"]
                    yield rx.toast(f"Error: {result['error']}", level="error")
                else:
                    self.result_data = json.dumps(result, indent=2)
                    yield rx.toast(
                        f"Run started with ID {result.get('run_id')}", level="success"
                    )
        except Exception as e:
            logging.exception(f"Unexpected error triggering job: {e}")
            async with self:
                self.error_message = str(e)
                yield rx.toast(f"Unexpected error: {e}", level="error")
        finally:
            async with self:
                self.is_loading = False