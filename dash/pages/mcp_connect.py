from dash import Dash, html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
from databricks.sdk.errors import DatabricksError
import dash
import json
from flask import request
import re

# pages/mcp_connect.py
dash.register_page(
    __name__,
    path='/ml/mcp-connect',
    title='Connect an MCP server',
    name='Connect an MCP server',
    category='AI / ML',
    icon='material-symbols:modeling'
)

# Global variable to store WorkspaceClient
w = None
# Global variable to store MCP session ID
mcp_session_id = None


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


def init_github_mcp(w):
    """Initialize GitHub MCP and get session ID"""
    global mcp_session_id
    try:
        init_json = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {}
        }
        
        response = w.serving_endpoints.http_request(
            conn="github_u2m_connection",
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            json=init_json,
        )
        
        # Extract the Mcp-Session-Id from response headers
        session_id = response.headers.get("mcp-session-id")
        if session_id:
            mcp_session_id = session_id
            return session_id, None
        else:
            return None, "No session ID returned by server"
            
    except Exception as e:
        return None, f"Error initializing MCP: {str(e)}"


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
            html.H1("AI / ML", className="mb-1"),
            html.P("Connect to remote MCP servers using Databricks Unity Catalog (UC) connections. This feature allows you to connect remote MCP servers like Slack, Jira, Gmail, Github or any service with an API using HTTP requests. ", className="text-muted mb-4"),
            html.P("You should set up your UC external connections in Databricks Unity Catalog first before testing them here.", className="text-muted mb-4"),
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
                                    id="connection-mcp-select",
                                    placeholder="Enter HTTP connection name...",
                                    className="form-control mb-2"
                                )
                            ], md=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Authentication mode:", className="form-label"),
                                dcc.Dropdown(
                                    id="auth-type-mcp-select",
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
                                    id="method-mcp-select",
                                    options=[
                                        {"label": "GET", "value": "GET"},
                                        {"label": "POST", "value": "POST"}
                                    ],
                                    value="POST",
                                    className="mb-2"
                                )
                            ], md=6),
                        ]),
                        dbc.Row([
                            # Request Body (JSON)
                            dbc.Col([
                                dbc.Label("JSON", className="form-label"),
                                dcc.Textarea(
                                    id="body-mcp-input",
                                    placeholder='{"key": "value"}',
                                    className="form-control",
                                    style={"height": "100px"}
                                )
                            ], width=6),
                        ]),
                        dbc.Button(
                            "Send Request",
                            id="send-request-btn",
                            color="primary",
                            className="mb-2"
                        ),
                        html.P("Note: App service principal must have USE CONNECTION privilege on UC connection object", className="text-dark small mb-2"),
                        html.Div(id="mcp-output", className="bg-light p-3 rounded")
                    ])
                ])
            ], label="Try it", tab_id="tab-try"),
            
            # Code snippet tab
            dbc.Tab([
                html.H4("OAuth User to Machine Per User (On-behalf-of-user)", className="mb-1", style={"margin-top": "0", "padding-top": "0"}),
                dcc.Markdown(
                    """```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json
from flask import request

token = request.headers.get("x-forwarded-access-token")
w = WorkspaceClient(token=token, auth_type="pat")


def init_mcp_session(w: WorkspaceClient, connection_name: str):
    init_payload = {
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {}
    }
    response = w.serving_endpoints.http_request(
        conn=connection_name,
        method=ExternalFunctionRequestHttpMethod.POST,
        path="/",
        json=init_payload,
    )
    return response.headers.get("mcp-session-id")


connection_name = "github_u2m_connection"
http_method = ExternalFunctionRequestHttpMethod.POST
path = "/"
headers = {"Content-Type": "application/json"}
payload = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}

session_id = init_mcp_session(w, connection_name)
headers["Mcp-Session-Id"] = session_id

response = w.serving_endpoints.http_request(
    conn=connection_name,
    method=http_method,
    path=path,
    headers=headers,
    json=payload,
)
print(response.json())
```""",
                    className="mb-3"
                ),
                html.H4("Bearer token", className="mb-1", style={"margin-top": "0", "padding-top": "0"}),
                dcc.Markdown(
                    """```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod


w = WorkspaceClient()

response = w.serving_endpoints.http_request(
    conn="github_u2m_connection",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/traffic/views",
    headers={"Accept": "application/vnd.github+json"},
    json={
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {}
    },
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
                            html.Li("mcp[cli]>=1.8.1"),
                            html.Li("fastapi>=0.115.12"),
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
    Output("mcp-output", "children", allow_duplicate=True),
    [Input("connection-mcp-select", "value"),
     Input("method-mcp-select", "value"),
     Input("auth-type-mcp-select", "value")],
    prevent_initial_call=True
)
def initialize_client(connection, method, auth_type):
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
    Output("mcp-output", "children", allow_duplicate=True),
    [Input("auth-type-mcp-select", "value")],
    prevent_initial_call=True
)
def reset_workspace_client_on_auth_change(auth_type):
    """Reset global workspace client when auth type changes"""
    global w
    w = None  # Reset the global workspace client
    return html.Div([html.P(f"Authentication type changed to: {auth_type}", className="text-info")])


@callback(
    Output("mcp-output", "children", allow_duplicate=True),
    [Input("send-request-btn", "n_clicks")],
    [State("connection-mcp-select", "value"),
     State("method-mcp-select", "value"),
     State("body-mcp-input", "value"),
     State("auth-type-mcp-select", "value")],
    prevent_initial_call=True
)
def send_external_request(n_clicks, connection, method, body, auth_type):
    if not all([connection, method]):
        return html.Div([html.P("Please fill in all required fields: Connection and Method", className="text-danger")])
    
    connection = connection.replace(" ", "")
    
    try:
        request_headers = {"Content-Type": "application/json"}
        
        # Parse body JSON
        request_data = None
        if body and body.strip():
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                return html.Div([html.P("❌ Invalid JSON in body", className="text-danger")])
        w = get_workspace_client(auth_type)
        if w is not None:
            method_enum = getattr(ExternalFunctionRequestHttpMethod, method)
            
            request_path = "/"
            
            # Initialize MCP if not already done
            global mcp_session_id
            if not mcp_session_id:
                session_id, error = init_github_mcp(w)
                if error:
                    # Check if this is a connection login error
                    if is_connection_login_error(error):
                        login_url = extract_login_url_from_error(error)
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
                                        id="retry-mcp-btn",
                                        color="secondary",
                                        n_clicks=0
                                    )
                                ], className="p-3 border border-warning rounded bg-light")
                            ], id="mcp-login-error")
                        else:
                            return html.Div([html.P(f"❌ MCP Initialization Error: {error}", className="text-danger")])
                    else:
                        return html.Div([html.P(f"❌ MCP Initialization Error: {error}", className="text-danger")])
                
                mcp_session_id = session_id
                
                # Add MCP session ID to headers
                request_headers["Mcp-Session-Id"] = mcp_session_id
                
                # Use json parameter for MCP requests
                response = w.serving_endpoints.http_request(
                    conn=connection, 
                    method=method_enum, 
                    path=request_path, 
                    headers=request_headers if request_headers else None, 
                    json=request_data if request_data else {},
                )
            else:
                # Regular requests
                if auth_type == "oauth_user_machine_per_user":
                    response = w.serving_endpoints.http_request(
                        conn=connection, 
                        method=method_enum, 
                        path=request_path, 
                        headers=request_headers if request_headers else None, 
                        json=request_data if request_data else {},
                    )
                else:
                    response = w.serving_endpoints.http_request(
                        conn=connection, 
                        method=method_enum, 
                        path=request_path, 
                        headers=request_headers if request_headers else None, 
                        json=request_data if request_data else {},
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
                ], id="mcp-login-error-main")
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
                ], id="mcp-login-error-main")
            else:
                return html.Div([html.P(f"❌ Error: {error_message}", className="text-danger")])
        else:
            return html.Div([html.P(f"❌ Error: {error_message}", className="text-danger")]) 

@callback(
    Output("mcp-output", "children", allow_duplicate=True),
    [Input("retry-mcp-btn", "n_clicks")],
    [State("connection-mcp-select", "value"),
     State("method-mcp-select", "value"),
     State("body-mcp-input", "value"),
     State("auth-type-mcp-select", "value")],
    prevent_initial_call=True
)
def retry_mcp_request(n_clicks, connection, method, body, auth_type):
    """Retry MCP request after user has logged in"""
    if not n_clicks:
        return no_update
    
    # Clear the session ID to force re-initialization
    global mcp_session_id
    mcp_session_id = None
    
    # Call the main request function
    return send_external_request(n_clicks, connection, method, body, auth_type) 