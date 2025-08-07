from dash import Dash, html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
from databricks.sdk.errors import DatabricksError
import dash
import json
from flask import request
import re

# pages/external_connections.py
dash.register_page(
    __name__,
    path='/external/connections',
    title='External Connections',
    name='External connections',
    category='External services',
    icon='material-symbols:link'
)

# Global variable to store WorkspaceClient
w = None


def get_workspace_client(auth_type):
    """Get or create WorkspaceClient with proper token handling based on auth type"""
    global w
    if w is None:
        try:
            if auth_type == "oauth_user_machine_per_user":
                # Get token from request context - this will only work during an actual request
                token = request.headers.get("x-forwarded-access-token")
                if token:
                    w = WorkspaceClient(
                        token=token, 
                        auth_type="pat"
                    )
                else:
                    # Fallback to default authentication
                    w = WorkspaceClient()
            elif auth_type == "oauth_machine_machine":
                # TODO: Add OAuth Machine to Machine logic
                w = WorkspaceClient()
            else:
                # Default fallback
                w = WorkspaceClient()
        except Exception:
            w = None
    return w


def extract_login_url_from_error(error_message):
    """Extract login URL from error message"""
    # Look for URL pattern in the error message
    url_pattern = r'https://[^\s]+/explore/connections/[^\s]+'
    match = re.search(url_pattern, error_message)
    if match:
        return match.group(0)
    return None


def is_connection_login_error(error_message):
    """Check if error is a connection login error"""
    return "Credential for user identity" in error_message and "Please login first to the connection" in error_message


def layout():
    return dbc.Container([
        # Header
        html.Div([
            html.H1("External Services", className="mb-1"),
            html.P("Connect to external APIs using Databricks Unity Catalog (UC) connections. This feature allows you to query external service data like Slack, Jira, Gmail, GitHub or any service with an API using HTTP requests. ", className="text-muted mb-4"),
            html.P("The 'Try it' example below is designed for GitHub regular connections. You should set up your UC external connections in Databricks Unity Catalog first before testing them here.", className="text-muted mb-4"),
        ], className="mb-4"),
        
        # Tabbed layout
        dbc.Tabs([
            # Try it tab
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Unity Catalog Connection name:", className="form-label"),
                                dcc.Input(
                                    id="connection-select",
                                    placeholder="Enter connection name...",
                                    className="form-control mb-2"
                                )
                            ], md=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Authentication mode:", className="form-label"),
                                dcc.Dropdown(
                                    id="auth-type-select",
                                    options=[
                                        {"label": "Bearer token", "value": "bearer_token"},
                                        {"label": "OAuth User to Machine Per User", "value": "oauth_user_machine_per_user"},
                                        {"label": "OAuth Machine to Machine", "value": "oauth_machine_machine"}
                                    ],
                                    value="oauth_user_machine_per_user",
                                    className="mb-2"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Label("HTTP method:", className="form-label"),
                                dcc.Dropdown(
                                    id="method-select",
                                    options=[
                                        {"label": "GET", "value": "GET"},
                                        {"label": "POST", "value": "POST"}
                                    ],
                                    value="GET",
                                    className="mb-2"
                                )
                            ], md=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Path:", className="form-label"),
                                dcc.Input(
                                    id="path-input",
                                    type="text",
                                    placeholder="/api/endpoint",
                                    className="form-control mb-2"
                                )
                            ], md=6),
                            # Request Body (JSON)
                            dbc.Col([
                                dbc.Label("Request data:", className="form-label"),
                                dcc.Textarea(
                                    id="body-input",
                                    placeholder='{"key": "value"}',
                                    className="form-control",
                                    style={"height": "100px"}
                                )
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Request headers:", className="form-label"),
                                dcc.Textarea(
                                    id="headers-input",
                                    placeholder='{"Content-Type": "application/json"}',
                                    className="form-control mb-2"
                                )
                            ], md=6),
                        ]),
                        dbc.Button(
                            "Send Request",
                            id="send-request-btn",
                            color="primary",
                            className="mb-2"
                        ),
                        html.P("Note: App service principal must have USE CONNECTION privilege on UC connection object", className="text-dark small mb-2"),
                        html.Div(id="response-output", className="bg-light p-3 rounded")
                    ])
                ])
            ], label="Try it", tab_id="tab-try"),
            
            # Code snippet tab
            dbc.Tab([
                html.H4("Bearer Token Method", className="mb-1", style={"margin-top": "0", "padding-top": "0"}),
                dcc.Markdown(
                    """```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
w = WorkspaceClient()

response = w.serving_endpoints.http_request(
    conn="github_connection",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/traffic/views",
    headers={"Accept": "application/vnd.github+json"},
)

print(response.json())
```""",
                    className="mb-3"
                ),
                html.H4("OAuth On-behalf-of-user", className="mb-1", style={"margin-top": "0", "padding-top": "0"}),
                dcc.Markdown(
                    """```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
from flask import request
token = request.headers.get("x-forwarded-access-token")
w = WorkspaceClient(token=token, auth_type="pat")

response = w.serving_endpoints.http_request(
    conn="github_u2m",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/user",
    headers={"Accept": "application/vnd.github+json"},
)

print(response.json())
```""",
                    className="mb-3"
                ),
            ], label="Code snippet", tab_id="tab-code"),
            
            # Requirements tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col(md=4, children=[
                        html.H5("Workspace Requirements", className="mb-2"),
                        html.Ul([
                            html.Li("Workspace enabled for Unity Catalog"),
                            html.Li("Metastore admin or CREATE CONNECTION privilege"),
                            html.Li("CREATE CATALOG permission on metastore"),
                            html.Li("USE CONNECTION privilege on connection object"),
                            html.Li("App service principal must have USE CONNECTION privilege on UC connection object")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Authentication Methods", className="mb-2"),
                        html.Ul([
                            html.Li("Bearer token (simple token-based)"),
                            html.Li("OAuth 2.0 Machine-to-Machine"),
                            html.Li("OAuth 2.0 User-to-Machine Shared"),
                            html.Li("OAuth 2.0 User-to-Machine Per User")
                        ])
                    ])
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col(md=6, children=[
                        html.H5("Databricks Resources", className="mb-2"),
                        html.Ul([
                            html.Li("Unity Catalog connection"),
                            html.Li("Foreign catalog (optional)"),
                            html.Li("Workspace access")
                        ])
                    ]),
                    dbc.Col(md=6, children=[
                        html.H5("Dependencies", className="mb-2"),
                        html.Ul([
                            html.Li("databricks-sdk>=0.60.0"),
                            html.Li("uvicorn>=0.34.2"),
                        ])
                    ])
                ]),
                html.Hr(),
                dbc.Row([
                    dbc.Col(children=[
                        html.H5("Setup Process", className="mb-2"),
                        html.Ol([
                            html.Li("Create Unity Catalog connection with authentication"),
                            html.Li("Configure host, port, base path, and credentials"),
                            html.Li("Test connection with http_request function"),
                            html.Li("Create foreign catalog (optional)"),
                            html.Li("Use in AI agent tools or direct API calls")
                        ])
                    ])
                ])
            ], label="Requirements", tab_id="tab-requirements")
        ], id="tabs", active_tab="tab-try")
    ], fluid=True)

# Callback to initialize WorkspaceClient when user first interacts with the page
@callback(
    Output("response-output", "children", allow_duplicate=True),
    [Input("connection-select", "value"),
     Input("method-select", "value"),
     Input("path-input", "value"),
     Input("auth-type-select", "value")],
    prevent_initial_call=True
)
def initialize_client(connection, rmethod, path, auth_type):
    """Initialize WorkspaceClient when user first interacts with form fields"""
    try:
        w = get_workspace_client(auth_type)
        if w is not None:
            return html.Div([html.P("✅ Connected to Databricks workspace", className="text-success")])
        else:
            return html.Div([html.P("⚠️ Unable to connect to Databricks workspace", className="text-warning")])
    except Exception as e:
        return html.Div([html.P(f"❌ Connection error: {str(e)}", className="text-danger")])


@callback(
    Output("response-output", "children", allow_duplicate=True),
    [Input("auth-type-select", "value")],
    prevent_initial_call=True
)
def reset_workspace_client_on_auth_change(auth_type):
    """Reset global workspace client when auth type changes"""
    global w
    w = None  # Reset the global workspace client
    return html.Div([html.P(f"Authentication type changed to: {auth_type}", className="text-info")])


@callback(
    Output("response-output", "children", allow_duplicate=True),
    [Input("send-request-btn", "n_clicks")],
    [State("connection-select", "value"),
     State("method-select", "value"),
     State("path-input", "value"),
     State("headers-input", "value"),
     State("body-input", "value"),
     State("auth-type-select", "value")],
    prevent_initial_call=True
)
def send_external_request(n_clicks, connection, method, path, headers, body, auth_type):
    if not all([connection, method]):
        return html.Div([html.P("Please fill in all required fields: Connection and Method", className="text-danger")])
    
    connection = connection.replace(" ", "")
    
    try:
        # Parse headers JSON
        headers_dict = {}
        if headers and headers.strip():
            try:
                headers_dict = json.loads(headers)
            except json.JSONDecodeError:
                return html.Div([html.P("❌ Invalid JSON in headers", className="text-danger")])
        
        # Parse body JSON
        body_data = None
        if body and body.strip():
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                return html.Div([html.P("❌ Invalid JSON in body", className="text-danger")])
        w = get_workspace_client(auth_type)
        if w is not None:
            method_enum = getattr(ExternalFunctionRequestHttpMethod, method)
            
            # Use empty string if no path provided
            request_path = path if path else ""
            
            if auth_type == "oauth_user_machine_per_user":
                response = w.serving_endpoints.http_request(
                    conn=connection, 
                    method=method_enum, 
                    path=request_path, 
                    headers=headers_dict, 
                    json=body_data
                )
            else:
                response = w.serving_endpoints.http_request(
                    conn=connection, 
                    method=method_enum, 
                    path=request_path, 
                    headers=headers_dict
                )
            
            response_json = response.json()
            return html.Div([
                html.H6("✅ Request Successful", className="text-success"),
                html.Pre(json.dumps(response_json, indent=2, default=str), className="bg-white p-2 rounded border")
            ])
        else:
            return html.Div([html.P("❌ Unable to connect to Databricks workspace", className="text-danger")])
    except DatabricksError as e:
        error_message = str(e)
        # Check if this is a connection login error
        if is_connection_login_error(error_message):
            login_url = extract_login_url_from_error(error_message)
            if login_url:
                return html.Div([
                    html.Div([
                        html.H6("🔐 Connection Login Required", className="text-warning mb-2"),
                        html.P("You need to authenticate with the external connection first.", className="mb-3"),
                        dbc.Button(
                            "Login to Connection",
                            href=login_url,
                            target="_blank",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Retry Request",
                            id="retry-request-btn",
                            color="secondary",
                            n_clicks=0
                        )
                    ], className="p-3 border border-warning rounded bg-light")
                ], id="connection-login-error-main")
            else:
                return html.Div([html.P(f"❌ Databricks Error: {error_message}", className="text-danger")])
        else:
            return html.Div([html.P(f"❌ Databricks Error: {error_message}", className="text-danger")])
    except Exception as e:
        error_message = str(e)
        # Check if this is a connection login error
        if is_connection_login_error(error_message):
            login_url = extract_login_url_from_error(error_message)
            if login_url:
                return html.Div([
                    html.Div([
                        html.H6("🔐 Connection Login Required", className="text-warning mb-2"),
                        html.P("You need to authenticate with the external connection first.", className="mb-3"),
                        dbc.Button(
                            "Login to Connection",
                            href=login_url,
                            target="_blank",
                            color="primary",
                            className="me-2"
                        ),
                        dbc.Button(
                            "Retry Request",
                            id="retry-request-btn",
                            color="secondary",
                            n_clicks=0
                        )
                    ], className="p-3 border border-warning rounded bg-light")
                ], id="connection-login-error-main")
            else:
                return html.Div([html.P(f"❌ Error: {error_message}", className="text-danger")])
        else:
            return html.Div([html.P(f"❌ Error: {error_message}", className="text-danger")]) 


@callback(
    Output("response-output", "children", allow_duplicate=True),
    [Input("retry-request-btn", "n_clicks")],
    [State("connection-select", "value"),
     State("method-select", "value"),
     State("path-input", "value"),
     State("headers-input", "value"),
     State("body-input", "value"),
     State("auth-type-select", "value")],
    prevent_initial_call=True
)
def retry_main_request(n_clicks, connection, method, path, headers, body, auth_type):
    """Retry main request after user has logged in"""
    if not n_clicks:
        return no_update
    
    # Call the main request function
    return send_external_request(n_clicks, connection, method, path, headers, body, auth_type) 