from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import dash

# pages/embed_dashboard.py
dash.register_page(
    __name__,
    path="/bi/dashboard",
    title="AI/BI Dashboard",
    name="AI/BI Dashboard",
    category="Business Intelligence",
    icon="material-symbols:dashboard",
)


def layout():
    return dbc.Container(
        [
            html.H1("Data Visualization", className="my-4"),
            html.H2("AI/BI Dashboard", className="mb-3"),
            html.P(
                [
                    "This recipe uses ",
                    html.A(
                        "Databricks AI/BI",
                        href="https://www.databricks.com/product/ai-bi",
                        target="_blank",
                    ),
                    " to embed a dashboard into a Databricks App.",
                ],
                className="mb-4",
            ),
            dbc.Tabs(
                [
                    # Try it tab
                    dbc.Tab(
                        label="Try it",
                        children=[
                            dbc.Form(
                                [
                                    dbc.Label("Embed the dashboard:", className="mt-3"),
                                    dbc.Input(
                                        id="iframe-source-input",
                                        type="text",
                                        placeholder="hhttps://dbc-f0e9b24f-3d49.cloud.databricks.com/embed/dashboardsv3/01eff8112e9411cd930f0ae0d2c6b63d?o=37581543725667790",
                                        style={
                                            "backgroundColor": "#f8f9fa",
                                            "border": "1px solid #dee2e6",
                                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)",
                                        },
                                    ),
                                    dbc.FormText(
                                        [
                                            "Find the correct embedding URL: ",
                                            html.A(
                                                "Embed a dashboard",
                                                href="https://docs.databricks.com/aws/en/dashboards/embed",
                                                target="_blank",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            html.Div(id="iframe-container", className="mt-4"),
                        ],
                        className="p-3",
                    ),
                    # Code snippet tab
                    dbc.Tab(
                        label="Code snippet",
                        children=[
                            dcc.Markdown(
                                """```python
from dash import html

iframe_source = "https://workspace.azuredatabricks.net/embed/dashboardsv3/dashboard-id"

html.Iframe(
    src=iframe_source,
    width="700px",
    height="600px",
    style={"border": "none"}
)
```""",
                                className="p-4 border rounded",
                            )
                        ],
                        className="p-3",
                    ),
                    # Requirements tab
                    dbc.Tab(
                        label="Requirements",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.H4(
                                                "Permissions (app service principal)",
                                                className="mb-3",
                                            ),
                                            html.Ul(
                                                [
                                                    dcc.Markdown(
                                                        "**```CAN VIEW```** on the dashboard"
                                                    )
                                                ],
                                                className="mb-4",
                                            ),
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            html.H4(
                                                "Databricks resources", className="mb-3"
                                            ),
                                            html.Ul(
                                                [html.Li("SQL Warehouse")],
                                                className="mb-4",
                                            ),
                                        ]
                                    ),
                                    dbc.Col(
                                        [
                                            html.H4("Dependencies", className="mb-3"),
                                            html.Ul(
                                                [
                                                    dcc.Markdown(
                                                        "* [Dash](https://pypi.org/project/dash/) - `dash`"
                                                    )
                                                ],
                                                className="mb-4",
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            dbc.Row(
                                dbc.Alert(
                                    "A workspace admin needs to enable dashboard embedding in the Security settings of your Databricks workspace for specific domains (e.g., databricksapps.com) or all domains for this sample to work.",
                                    color="warning",
                                )
                            ),
                        ],
                        className="p-3",
                    ),
                ],
                className="mb-4",
            ),
        ],
        fluid=True,
        className="py-4",
    )


@callback(
    Output("iframe-container", "children"),
    [Input("iframe-source-input", "value")],
    prevent_initial_call=True,
)
def update_iframe(iframe_source):
    if not iframe_source:
        return None

    return html.Iframe(
        src=iframe_source,
        width="700px",
        height="600px",
        style={
            "border": "none",
            "borderRadius": "4px",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        },
    )


# Make layout available at module level
__all__ = ["layout"]
