import base64
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
import dash

# pages/secrets_retrieve.py
dash.register_page(
    __name__,
    path="/secrets/retrieve",
    title="Secrets Retrieve",
    name="Retrieve a secret",
    category="Authentication",
    icon="material-symbols:key",
)


w = WorkspaceClient()


def get_secret(scope, key):
    try:
        secret_response = w.secrets.get_secret(scope=scope, key=key)
        decoded_secret = base64.b64decode(secret_response.value).decode("utf-8")
        return decoded_secret
    except Exception:
        return None


def layout():
    return dbc.Container(
        [
            html.H1("Secrets", className="my-4"),
            html.H2("Retrieve a secret", className="mb-3"),
            html.P(
                [
                    "This recipe retrieves a ",
                    html.A(
                        "Databricks secret",
                        href="https://docs.databricks.com/en/security/secrets/index.html",
                        target="_blank",
                    ),
                    ". Use secrets to securely connect to external services and APIs.",
                ],
                className="mb-4",
            ),
            dbc.Tabs(
                [
                    # Try it tab
                    dbc.Tab(
                        [
                            dbc.Form(
                                [
                                    dbc.Label("Secret scope:", className="mt-3"),
                                    dbc.Input(
                                        id="scope-input",
                                        type="text",
                                        placeholder="apis",
                                        style={
                                            "backgroundColor": "#f8f9fa",
                                            "border": "1px solid #dee2e6",
                                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)",
                                        },
                                    ),
                                    dbc.Label("Secret name (key):", className="mt-3"),
                                    dbc.Input(
                                        id="key-input",
                                        type="text",
                                        placeholder="weather_service_key",
                                        style={
                                            "backgroundColor": "#f8f9fa",
                                            "border": "1px solid #dee2e6",
                                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)",
                                        },
                                    ),
                                    dbc.Button(
                                        "Retrieve",
                                        id="retrieve-button",
                                        color="primary",
                                        className="mt-3",
                                    ),
                                ]
                            ),
                            html.Div(id="secret-output", className="mt-4"),
                        ],
                        label="Try it",
                        tab_id="tab-1",
                    ),
                    # Code snippet tab
                    dbc.Tab(
                        [
                            dcc.Markdown(
                                """```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_secret(scope, key):
    try:
        secret_response = w.secrets.get_secret(scope=scope, key=key)
        decoded_secret = base64.b64decode(secret_response.value).decode('utf-8')
        return decoded_secret
    except Exception as e:
        print("Secret not found or inaccessible")

scope_name = "my_secret_scope"
secret_key = "api_key"
secret = get_secret(scope_name, secret_key)
```""",
                                className="border rounded p-3",
                            )
                        ],
                        label="Code snippet",
                        tab_id="tab-2",
                    ),
                    # Requirements tab
                    dbc.Tab(
                        [
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
                                                        "**```CAN READ```** on the secret scope"
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
                                                [html.Li("Secret scope")],
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
                                                        "* [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`"
                                                    ),
                                                    dcc.Markdown(
                                                        "* [Dash](https://pypi.org/project/dash/) - `dash`"
                                                    ),
                                                ],
                                                className="mb-4",
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        label="Requirements",
                        tab_id="tab-3",
                    ),
                ],
                id="tabs",
                active_tab="tab-1",
                className="mb-4",
            ),
        ],
        fluid=True,
        className="py-4",
    )


@callback(
    Output("secret-output", "children"),
    [Input("retrieve-button", "n_clicks")],
    [State("scope-input", "value"), State("key-input", "value")],
    prevent_initial_call=True,
)
def update_output(n_clicks, scope, key):
    if not all([scope, key]):
        return dbc.Alert("Please fill in all fields", color="warning")

    secret = get_secret(scope, key)
    if secret is not None:
        return dbc.Alert(
            "Secret retrieved! The value is securely handled in the backend.",
            color="success",
        )
    return dbc.Alert(
        "Secret not found or inaccessible. Please create a secret scope and key before retrieving.",
        color="danger",
    )


__all__ = ["layout"]
