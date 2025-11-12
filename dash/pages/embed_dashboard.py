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
    return dbc.Container([
        # Header section matching Streamlit style
        dbc.Row([
            dbc.Col([
                html.H1("Data Visualization", className="mb-1"),
                html.Hr(className="mb-2"),
                html.H2("AI/BI Dashboard", className="mb-2"),
                html.P([
                    "This recipe uses ",
                    html.A(
                        "Databricks AI/BI",
                        href="https://www.databricks.com/product/ai-bi",
                        target="_blank",
                        className="text-primary"
                    ),
                    " to embed a dashboard into a Databricks App."
                ], className="mb-3")
            ])
        ]),
        
        # Tabbed layout
        dbc.Tabs([
                    # Try it tab
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Embed the dashboard:", className="form-label"),
                        dcc.Input(
                                        id="iframe-source-input",
                                        type="text",
                            placeholder="https://dbc-f0e9b24f-3d49.cloud.databricks.com/embed/dashboardsv3/01eff8112e9411cd930f0ae0d2c6b63d?o=37581543725667790",
                            className="form-control mb-2"
                        ),
                        html.Small([
                                            "Find the correct embedding URL: ",
                                            html.A(
                                                "Embed a dashboard",
                                                href="https://docs.databricks.com/aws/en/dashboards/embed",
                                                target="_blank",
                                className="text-primary"
                                    ),
                        ], className="text-muted"),
                        html.Div(id="iframe-container", className="mt-3")
                    ])
                ])
            ], label="Try it", tab_id="tab-try"),
            
                    # Code snippet tab
            dbc.Tab([
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
                    className="mb-0"
                            )
            ], label="Code snippet", tab_id="tab-code"),
            
                    # Requirements tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col(md=4, children=[
                        html.H5("Permissions", className="mb-2"),
                        html.Ul([
                            html.Li("Dashboard access permissions"),
                            html.Li("Embedding URL access")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Databricks Resources", className="mb-2"),
                        html.Ul([
                            html.Li("AI/BI Dashboard"),
                            html.Li("Embedding URL")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Dependencies", className="mb-2"),
                        html.Ul([
                            html.Li("dash"),
                            html.Li("dash-bootstrap-components")
                        ])
                    ])
                ])
            ], label="Requirements", tab_id="tab-requirements")
        ], id="tabs", active_tab="tab-try")
    ], fluid=True)

@callback(
    Output("iframe-container", "children"),
    [Input("iframe-source-input", "value")],
    prevent_initial_call=True,
)
def update_iframe(iframe_source):
    if iframe_source:
            return html.Iframe(
            src=iframe_source,
            width="100%",
            height="600px",
            style={"border": "none", "borderRadius": "4px"}
        )
    return html.Div("Enter a dashboard URL to embed it here.", className="text-muted")


# Make layout available at module level
__all__ = ["layout"]
