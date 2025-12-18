import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.retrieve_job_results_state import RetrieveJobResultsState
from app import theme

CODE_SNIPPET = """import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class RetrieveJobResultsState(rx.State):
    task_run_id: str = ""
    results: str = ""
    is_loading: bool = False
    error_message: str = ""

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
"""


def retrieve_job_results_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                "* `CAN VIEW` permission on the job", class_name="text-sm text-gray-600"
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


def retrieve_job_results_content() -> rx.Component:
    """Content for the 'Try It' tab of the Retrieve Job Results page."""
    return rx.vstack(
        rx.vstack(
            rx.text("Specify a run ID:", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="293894477334278",
                on_change=RetrieveJobResultsState.set_task_run_id,
                class_name="w-full",
                default_value=RetrieveJobResultsState.task_run_id,
            ),
            width="100%",
        ),
        rx.button(
            "Get task run results",
            on_click=RetrieveJobResultsState.get_results,
            is_loading=RetrieveJobResultsState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
        ),
        rx.cond(
            RetrieveJobResultsState.sql_output,
            rx.vstack(
                rx.markdown("### SQL Output"),
                rx.code_block(
                    RetrieveJobResultsState.sql_output,
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        rx.cond(
            RetrieveJobResultsState.dbt_output,
            rx.vstack(
                rx.markdown("### dbt Output"),
                rx.code_block(
                    RetrieveJobResultsState.dbt_output,
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        rx.cond(
            RetrieveJobResultsState.run_job_output,
            rx.vstack(
                rx.markdown("### Run Job Output"),
                rx.code_block(
                    RetrieveJobResultsState.run_job_output,
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        rx.cond(
            RetrieveJobResultsState.notebook_output,
            rx.vstack(
                rx.markdown("### Notebook Output"),
                rx.code_block(
                    RetrieveJobResultsState.notebook_output,
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        rx.cond(
            RetrieveJobResultsState.error_message,
            rx.box(
                rx.hstack(
                    rx.icon("triangle-alert", class_name="text-red-500"),
                    rx.text(
                        RetrieveJobResultsState.error_message, class_name="text-red-500"
                    ),
                ),
                class_name="p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def retrieve_job_results_page() -> rx.Component:
    """The Retrieve Job Results sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Retrieve Job Results",
            page_description="Check the status of a Databricks Job run and retrieve its output or final state.",
            try_it_content=retrieve_job_results_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=retrieve_job_results_requirements,
        )
    )