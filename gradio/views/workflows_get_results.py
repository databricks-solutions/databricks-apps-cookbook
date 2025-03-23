import gradio as gr
from databricks.sdk import WorkspaceClient

def get_task_results(task_run_id):
    if not task_run_id.strip():
        return "⚠️ Please specify a valid task run ID."
    
    w = WorkspaceClient()
    try:
        results = w.jobs.get_run_output(task_run_id)
        output = ["✅ Task run results retrieved successfully\n"]
        
        if results.sql_output:
            output.append("SQL output:")
            output.append(str(results.sql_output.as_dict()))
        
        if results.dbt_output:
            output.append("\ndbt output:")
            output.append(str(results.dbt_output.as_dict()))
            
        if results.run_job_output:
            output.append("\nNotebook output:")
            output.append(str(results.run_job_output.as_dict()))
            
        if results.notebook_output:
            output.append("\nNotebook output:")
            output.append(str(results.notebook_output.as_dict()))
            
        return "\n".join(output)
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create the interface
with gr.Blocks() as demo:
    gr.Markdown("# Workflows")
    gr.Markdown("## Retrieve job results")
    gr.Markdown("This recipe retrieves the results of a [Databricks Workflows](https://docs.databricks.com/en/jobs/index.html) job task run.")
    
    with gr.Tab("Try it"):
        task_input = gr.Textbox(
            label="Specify a task run ID:",
            placeholder="293894477334278"
        )
        submit_btn = gr.Button("Get task run results")
        output = gr.Textbox(label="Results", lines=10)
        
        submit_btn.click(
            fn=get_task_results,
            inputs=task_input,
            outputs=output
        )
    
    with gr.Tab("Code snippet"):
        gr.Code("""
import gradio as gr
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
results = w.jobs.get_run_output(task_run_id)
print(results)
        """, language="python")
    
    with gr.Tab("Requirements"):
        gr.Markdown("""
| Permissions (app service principal) | Databricks resources | Dependencies |
|-----------------------------------|---------------------|--------------|
| • `Can view` permission on the job | • Job | • [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`<br>• [Gradio](https://pypi.org/project/gradio/) - `gradio` |

See [Control access to a job](https://docs.databricks.com/en/jobs/privileges.html#control-access-to-a-job) for more information.
        """)

if __name__ == "__main__":
    demo.launch()