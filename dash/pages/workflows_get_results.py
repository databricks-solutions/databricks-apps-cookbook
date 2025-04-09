from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
import json
import dash

# pages/workflows_get_results.py
dash.register_page(
    __name__,
    path='/workflows/get-results',
    title='Retrieve job results',
    name='Retrieve job results',
    category='Workflows',
    icon='material-symbols:list-alt'
)


w = WorkspaceClient()

def layout():
    return dbc.Container([
        html.H1("Workflows", className="my-4"),
        html.H2("Retrieve job results", className="mb-3"),
        html.P([
            "This recipe retrieves the results of a ",
            html.A(
                "Databricks Workflows",
                href="https://docs.databricks.com/en/jobs/index.html",
                target="_blank"
            ),
            " job task run."
        ], className="mb-4"),
        
        dbc.Tabs([
            # Try it tab
            dbc.Tab(label="Try it", tab_id="try-it", children=[
                dbc.Form([
                    dbc.Label("Specify a task run ID:", className="mt-3"),
                    dbc.Input(
                        id="task-run-input",
                        type="text",
                        placeholder="293894477334278",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    
                    dbc.Button(
                        "Get task run results",
                        id="get-results-button",
                        color="primary",
                        className="mt-3"
                    ),
                ]),
                html.Div(id="results-output", className="mt-4")
            ], className="p-3"),
            
            # Code snippet tab
            dbc.Tab(label="Code snippet", children=[
                dcc.Markdown('''```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

task_run_id = "293894477334278"
results = w.jobs.get_run_output(task_run_id)

print(results)
```''', className="p-4 border rounded")
            ], className="p-3"),
            
            # Requirements tab
            dbc.Tab(label="Requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```CAN VIEW```** on the job")
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

def format_output_section(title, data):
    if not data:
        return None
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="mb-3"),
            dcc.Markdown(f"```json\n{json.dumps(data.as_dict(), indent=2)}\n```")
        ]),
        className="mb-3"
    )

@callback(
    Output("results-output", "children"),
    [Input("get-results-button", "n_clicks")],
    [State("task-run-input", "value")],
    prevent_initial_call=True
)
def update_results(n_clicks, task_run_id):
    if not task_run_id or not task_run_id.strip():
        return dbc.Alert(
            "Please specify a valid task run ID.",
            color="warning"
        )
    
    try:
        results = w.jobs.get_run_output(task_run_id)
        output_sections = []
        
        # Success message
        output_sections.append(
            dbc.Alert(
                "Task run results retrieved successfully",
                color="success",
                className="mb-3"
            )
        )
        
        # Add each type of output if present
        if results.sql_output:
            output_sections.append(format_output_section("SQL output", results.sql_output))
        
        if results.dbt_output:
            output_sections.append(format_output_section("dbt output", results.dbt_output))
            
        if results.run_job_output:
            output_sections.append(format_output_section("Run job output", results.run_job_output))
            
        if results.notebook_output:
            output_sections.append(format_output_section("Notebook output", results.notebook_output))
            
        return html.Div(output_sections)
        
    except Exception as e:
        return dbc.Alert(
            f"Error retrieving results: {str(e)}",
            color="danger"
        )

# Make layout available at module level
__all__ = ['layout']
