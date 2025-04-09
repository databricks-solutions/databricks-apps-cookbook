import json
import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

st.header(body="Workflows", divider=True)
st.subheader("Run a job")

st.write(
    "This recipe triggers a [Databricks Workflows](https://docs.databricks.com/en/jobs/index.html) job."
)

tab1, tab2, tab3 = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])


def trigger_workflow(job_id: str, parameters: dict):
    try:
        run = w.jobs.run_now(job_id=job_id, job_parameters=parameters)
        return {
            "run_id": run.run_id,
            "state": "Triggered",
        }
    except Exception as e:
        return {"error": str(e)}


if "workflow_trigger_success" not in st.session_state:
    st.session_state.workflow_trigger_success = False

with tab1:
    job_id = st.text_input(
        label="Specify job id:",
        placeholder="921773893211960",
        help="You can find the job ID under job details after opening a job in the UI.",
    )

    parameters_input = st.text_area(
        label="Specify job parameters as JSON:",
        placeholder='{"param1": "value1", "param2": "value2"}',
    )

    if st.button(label="Trigger job"):
        if not job_id.strip():
            st.warning("Please specify a valid job ID.", icon="⚠️")
        elif not parameters_input.strip():
            st.warning("Please specify input parameters.", icon="⚠️")
        else:
            try:
                parameters = json.loads(parameters_input.strip())
                results = trigger_workflow(job_id.strip(), parameters)
                if "error" in results:
                    st.error(
                        f"Error triggering workflow: {results['error']}", icon="🚨"
                    )
                else:
                    st.success("Workflow triggered successfully", icon="✅")
                    st.json(results)
            except Exception as e:
                st.error(f"Error parsing input parameters: {e}", icon="🚨")

with tab2:
    st.code("""
    import json
    import streamlit as st
    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()

    job_id = st.text_input(
        label="Specify job id:",
        placeholder="921773893211960",
        help="You can find the job ID under job details after opening a job in the UI.",
    )

    parameters_input = st.text_area(
        label="Specify job parameters as JSON:",
        placeholder='{"param1": "value1", "param2": "value2"}',
    )

    parameters = json.loads(parameters_input.strip())

    if st.button(label="Trigger job"):
        try:
            run = w.jobs.run_now(job_id=job_id, job_parameters=parameters)
            st.text(f"Started run with ID {run.run_id}")
        except Exception as e:
            st.warning(e)
    """)

with tab3:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `CAN MANAGE RUN` permission on the job

                    See [Control access to a job](https://docs.databricks.com/en/jobs/privileges.html#control-access-to-a-job) for more information.
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Job
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
