---
name: cookbook-workflows
description: "Trigger and monitor Databricks Workflows jobs from Databricks Apps. Use when the user wants to run a job, pass parameters, or retrieve job run results from a Dash, Streamlit, or Reflex app."
---

# Workflows

Trigger [Databricks Workflows](https://docs.databricks.com/en/jobs/index.html) jobs and retrieve run results using the [Databricks SDK](https://databricks-sdk-py.readthedocs.io/en/latest/).

## Recipes

### Trigger a job

#### Dash

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

job_id = "921773893211960"
parameters = {"param1": "value1", "param2": "value2"}

try:
    run = w.jobs.run_now(job_id=job_id, job_parameters=parameters)
    print(f"Started run with ID {run.run_id}")
except Exception as e:
    print(f"Error: {e}")
```

#### Streamlit

```python
import streamlit as st
import json
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

job_id = st.text_input("Job ID:", placeholder="921773893211960")
parameters_input = st.text_area("Parameters (JSON):", placeholder='{"param1": "value1"}')

if st.button("Trigger job"):
    try:
        params = json.loads(parameters_input.strip()) if parameters_input.strip() else {}
        run = w.jobs.run_now(job_id=job_id, job_parameters=params)
        st.success(f"Started run with ID {run.run_id}")
    except Exception as e:
        st.warning(str(e))
```

#### Reflex

```python
import reflex as rx
import json
from databricks.sdk import WorkspaceClient

class TriggerJobState(rx.State):
    job_id: str = ""
    parameters_input: str = ""
    result_data: str = ""

    @rx.event(background=True)
    async def trigger_job(self):
        w = WorkspaceClient()
        params = json.loads(self.parameters_input.strip()) if self.parameters_input.strip() else {}
        result = w.jobs.run_now(job_id=int(self.job_id), job_parameters=params)
        async with self:
            self.result_data = json.dumps({"run_id": result.run_id}, indent=2)
```

### Retrieve job run results

#### Dash

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

task_run_id = "293894477334278"
results = w.jobs.get_run_output(task_run_id)
print(results)
```

#### Streamlit

```python
import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

task_run_id = st.text_input("Task run ID:", placeholder="293894477334278")
if task_run_id:
    results = w.jobs.get_run_output(task_run_id)
    st.text(results)
```

#### Reflex

```python
import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class RetrieveJobResultsState(rx.State):
    run_id: str = ""
    results: str = ""

    @rx.event(background=True)
    async def get_results(self):
        run_output = w.jobs.get_run_output(run_id=int(self.run_id))
        async with self:
            self.results = str(run_output)
```

## Resources

- [Databricks Job](https://docs.databricks.com/aws/en/jobs/configure-job)

## Permissions

| Action | Permission |
|--------|-----------|
| Trigger a job | `CAN MANAGE RUN` on the job |
| Retrieve results | `CAN VIEW` on the job |

See [Control access to a job](https://docs.databricks.com/en/jobs/privileges.html#control-access-to-a-job).

## Dependencies

```
databricks-sdk
```

Plus your framework package (`dash`, `streamlit`, or `reflex`).

## Common Pitfalls

- Use `json.loads()` instead of `eval()` for parsing user-provided JSON parameters
- `run_now()` returns immediately; the job runs asynchronously. Use `run_now_and_wait()` to block until completion
- `get_run_output()` takes a task run ID, not the job run ID
