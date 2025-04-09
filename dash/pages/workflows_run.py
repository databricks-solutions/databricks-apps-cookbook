from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
import json
import dash

# pages/workflows_run.py
dash.register_page(
    __name__,
    path='/workflows/run',
    title='Workflows Run',
    name='Trigger a job',
    category='Workflows',
    icon='material-symbols:play-circle'
)

w = WorkspaceClient()

def trigger_workflow(job_id: str, parameters: dict):
    try:
        run = w.jobs.run_now(job_id=job_id, job_parameters=parameters)
        return {
            "run_id": run.run_id,
            "state": "Triggered",
        }
    except Exception as e:
        return {"error": str(e)}

def layout():
    return dbc.Container([
        html.H1("Workflows", className="my-4"),
        html.H2("Run a job", className="mb-3"),
        html.P([
            "This recipe triggers a ",
            html.A(
                "Databricks Workflows",
                href="https://docs.databricks.com/en/jobs/index.html",
                target="_blank"
            ),
            " job."
        ], className="mb-4"),
        
        dbc.Tabs([
            # Try it tab
            dbc.Tab(label="Try it", tab_id="try-it",  children=[
                dbc.Form([
                    dbc.Label("Specify job id:", className="mt-3"),
                    dbc.Input(
                        id="job-id-input",
                        type="text",
                        placeholder="921773893211960",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    
                    dbc.Label("Specify job parameters as JSON:", className="mt-3"),
                    dbc.Textarea(
                        id="parameters-input",
                        placeholder='{"param1": "value1", "param2": "value2"}',
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    
                    dbc.Button(
                        "Trigger job",
                        id="trigger-button",
                        color="primary",
                        className="mt-3"
                    ),
                ]),
                html.Div(id="trigger-output", className="mt-4")
            ], className="p-3"),
            
            # Code snippet tab
            dbc.Tab(label="Code snippet", children=[
                dcc.Markdown('''```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

job_id = "921773893211960"
parameters = {"param1": "value1", "param2": "value2"}

try:
    run = w.jobs.run_now(job_id=job_id, job_parameters=parameters)
    print(f"Started run with ID {run.run_id}")
except Exception as e:
    print(f"Error: {e}")
```''', className="p-4 border rounded")
            ], className="p-3"),
            
            # Requirements tab
            dbc.Tab(label="Requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```CAN MANAGE RUN```** on the job")
                        ], className="mb-4"),
                        html.P([
                            "See ",
                            html.A(
                                "Control access to a job",
                                href="https://docs.databricks.com/en/jobs/privileges.html#control-access-to-a-job",
                                target="_blank"
                            ),
                            " for more information."
                        ])
                    ]),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.Ul([
                            html.Li("Job")
                        ], className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Dependencies", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("* [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`"),
                            dcc.Markdown("* [Dash](https://pypi.org/project/dash/) - `dash`")
                        ], className="mb-4")
                    ])
                ])
            ], className="p-3")
        ], className="mb-4", active_tab="try-it")
    ], fluid=True, className="py-4")

@callback(
    Output("trigger-output", "children"),
    [Input("trigger-button", "n_clicks")],
    [State("job-id-input", "value"),
     State("parameters-input", "value")],
    prevent_initial_call=True
)
def update_output(n_clicks, job_id, parameters_input):
    if not job_id or not job_id.strip():
        return dbc.Alert(
            "Please specify a valid job ID.",
            color="warning"
        )
    
    if not parameters_input or not parameters_input.strip():
        return dbc.Alert(
            "Please specify input parameters.",
            color="warning"
        )
    
    try:
        parameters = json.loads(parameters_input)
        results = trigger_workflow(job_id.strip(), parameters)
        
        if "error" in results:
            return dbc.Alert(
                f"Error triggering workflow: {results['error']}",
                color="danger"
            )
        else:
            return html.Div([
                dbc.Alert(
                    "Workflow triggered successfully",
                    color="success",
                    className="mb-3"
                ),
                dbc.Card(
                    dbc.CardBody([
                        dcc.Markdown(f"```json\n{json.dumps(results, indent=2)}\n```")
                    ])
                )
            ])
            
    except json.JSONDecodeError as e:
        return dbc.Alert(
            f"Error parsing input parameters: Invalid JSON format - {str(e)}",
            color="danger"
        )
    except Exception as e:
        return dbc.Alert(
            f"Error: {str(e)}",
            color="danger"
        )

# Make layout available at module level
__all__ = ['layout']
