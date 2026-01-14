import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.components.loading_spinner import loading_spinner
from app.states.trigger_job_state import TriggerJobState
from app import theme

CODE_SNIPPET = """import reflex as rx
import json
from databricks.sdk import WorkspaceClient

def trigger_workflow(job_id: str, params: dict):
    w = WorkspaceClient()
    try:
        run = w.jobs.run_now(job_id=int(job_id), job_parameters=params)
        return {"run_id": run.run_id, "state": "Triggered"}
    except Exception as e:
        return {"error": str(e)}

class TriggerJobState(rx.State):
    job_id: str = ""
    parameters_input: str = ""
    result_data: str = ""
    error_message: str = ""
    is_loading: bool = False

    @rx.event(background=True)
    async def trigger_job(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.result_data = ""

            if not self.job_id:
                yield rx.toast("Please specify a Job ID.", level="warning")
                self.is_loading = False
                return

        try:
            params = json.loads(self.parameters_input.strip())
            result = trigger_workflow(self.job_id, params)

            async with self:
                if "error" in result:
                    self.error_message = result["error"]
                    yield rx.toast(f"Error: {result['error']}", level="error")
                else:
                    self.result_data = json.dumps(result, indent=2)
                    yield rx.toast(f"Run started: {result.get('run_id')}", level="success")
        except json.JSONDecodeError:
             async with self:
                yield rx.toast("Invalid JSON parameters", level="error")
        except Exception as e:
             async with self:
                self.error_message = str(e)
        finally:
             async with self:
                self.is_loading = False
"""


def trigger_job_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
* `CAN MANAGE RUN` on the Job
""",
                class_name="text-sm text-gray-600",
            ),
            rx.link(
                "Job permissions documentation",
                href="https://docs.databricks.com/en/security/auth-authz/access-control/jobs-acl.html#job-permissions",
                is_external=True,
                class_name="text-sm text-blue-600 hover:underline",
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
            rx.markdown("* Job", class_name="text-sm text-gray-600"),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* `databricks-sdk`
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


def trigger_job_content() -> rx.Component:
    """Content for the 'Try It' tab of the Trigger Job page."""
    return rx.vstack(
        rx.vstack(
            rx.text("Specify job id:", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="921773893211960",
                on_change=TriggerJobState.set_job_id,
                class_name="w-full",
                default_value=TriggerJobState.job_id,
            ),
            rx.text(
                "Find the Job ID in the URL of your job: /jobs/<job-id>/...",
                class_name="text-xs text-gray-500",
            ),
            width="100%",
            spacing="1",
        ),
        rx.vstack(
            rx.text(
                "Specify job parameters as JSON (optional):",
                class_name="font-semibold text-sm",
            ),
            rx.text_area(
                placeholder='{"key": "value"} or leave empty',
                on_change=TriggerJobState.set_parameters_input,
                class_name="w-full h-32 font-mono text-sm",
                default_value=TriggerJobState.parameters_input,
            ),
            width="100%",
        ),
        rx.button(
            "Trigger job",
            on_click=TriggerJobState.trigger_job,
            is_loading=TriggerJobState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
        ),
        rx.cond(TriggerJobState.is_loading, loading_spinner("Triggering job...")),
        rx.cond(
            TriggerJobState.error_message,
            rx.box(
                rx.hstack(
                    rx.icon("triangle-alert", class_name="text-red-500"),
                    rx.text(TriggerJobState.error_message, class_name="text-red-500"),
                ),
                class_name="p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            TriggerJobState.result_data,
            rx.vstack(
                rx.text(
                    "Run started successfully:",
                    class_name="font-semibold text-green-700",
                ),
                rx.code_block(
                    TriggerJobState.result_data, language="json", class_name="w-full"
                ),
                class_name="p-4 bg-green-50 border border-green-200 rounded-lg w-full",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def trigger_job_page() -> rx.Component:
    """The Trigger a Job sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Trigger a Databricks Job",
            page_description="Programmatically start a new run of an existing Databricks Job and get the run ID.",
            try_it_content=trigger_job_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=trigger_job_requirements,
        )
    )