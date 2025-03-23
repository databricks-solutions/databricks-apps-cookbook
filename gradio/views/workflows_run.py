import json
import gradio as gr
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def trigger_workflow(job_id: str, parameters: str):
    if not job_id.strip():
        return "⚠️ Please specify a valid job ID."
    elif not parameters.strip():
        return "⚠️ Please specify input parameters."
    
    try:
        parameters_dict = json.loads(parameters.strip())
        run = w.jobs.run_now(job_id=job_id, job_parameters=parameters_dict)
        return f"✅ Workflow triggered successfully\nRun ID: {run.run_id}\nState: Triggered"
    except json.JSONDecodeError as e:
        return f"🚨 Error parsing input parameters: {e}"
    except Exception as e:
        return f"🚨 Error triggering workflow: {e}"

# Create the interface
demo = gr.Interface(
    fn=trigger_workflow,
    inputs=[
        gr.Textbox(
            label="Job ID",
            placeholder="921773893211960",
            info="You can find the job ID under job details after opening a job in the UI."
        ),
        gr.Textbox(
            label="Job Parameters (JSON)",
            placeholder='{"param1": "value1", "param2": "value2"}',
            lines=5
        )
    ],
    outputs=gr.Textbox(label="Result"),
    title="Databricks Workflow Runner",
    description="This application triggers a Databricks Workflows job.",
    article="""
    ### Requirements:
    
    **Permissions (app service principal)**
    * `CAN MANAGE RUN` permission on the job
    
    **Databricks resources**
    * Job
    
    **Dependencies**
    * Databricks SDK for Python (`databricks-sdk`)
    * Gradio (`gradio`)
    """
)

if __name__ == "__main__":
    demo.launch()