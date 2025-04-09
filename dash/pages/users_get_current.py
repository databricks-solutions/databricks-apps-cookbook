from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from flask import request
import dash

# pages/users_get_current.py
dash.register_page(
    __name__,
    path='/users/get-current',
    title='Get current user',
    name='Get current user',
    category='Authentication',
    icon='material-symbols:person'
)



def layout():
    return dbc.Container([
        html.H1("Users", className="my-4"),
        html.H2("Get current user", className="mb-3"),
        html.P([
            "This recipe gets information about the user accessing this Databricks App from their ",
            html.A(
                "HTTP headers",
                href="https://docs.databricks.com/en/dev-tools/databricks-apps/app-development.html#what-http-headers-are-passed-to-databricks-apps",
                target="_blank"
            ),
            "."
        ], className="mb-4"),
        
        dbc.Tabs([
            dbc.Tab(label="Try it", tab_id="tab-1", children=[
                html.Div([
                    html.H4("User Details", className="mb-3"),
                    dbc.Spinner(
                        dbc.Row([
                            dbc.Col([
                                html.P([
                                    html.Strong("E-mail: "), 
                                    html.Span(id="user-email-current")
                                ]),
                                html.P([
                                    html.Strong("Username: "), 
                                    html.Span(id="user-name-current")
                                ]),
                                html.P([
                                    html.Strong("User: "), 
                                    html.Span(id="user-user-current")
                                ]),
                                html.P([
                                    html.Strong("IP Address: "), 
                                    html.Span(id="user-ip-current")
                                ])
                            ])
                        ]),
                        color="primary",
                        type="border",
                    ),
                    html.H4("All Headers", className="mt-4 mb-3"),
                    dbc.Spinner(
                        html.Pre(id="all-headers-current", style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '1rem',
                            'borderRadius': '0.25rem',
                            'maxHeight': '400px',
                            'overflowY': 'auto',
                            'whiteSpace': 'pre-wrap',
                            'wordBreak': 'break-word'
                        }),
                        color="primary",
                        type="border",
                    )
                ], className="p-3")
            ], className="p-3"),
            
            dbc.Tab(label="Code snippet", tab_id="tab-2", children=[
                dcc.Markdown('''```python
from flask import request
headers = request.headers
email = headers.get("X-Forwarded-Email")
username = headers.get("X-Forwarded-Preferred-Username")
user = headers.get("X-Forwarded-User")
ip = headers.get("X-Real-Ip")
print(f"E-mail: {email}, username: {username}, user: {user}, ip: {ip}")
```''', className="p-4 border rounded"),
                dbc.Alert([
                    html.H4("Other frameworks", className="alert-heading"),
                    html.P([
                        "Streamlit: use ",
                        html.Code("st.context.headers"),
                        " from the Streamlit library."
                    ])
                ], color="info", className="mt-3")
            ], className="p-3"),
            
            dbc.Tab(label="Requirements", tab_id="tab-3", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.P("No permissions needed", className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.P("None", className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Dependencies", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("* [Dash](https://pypi.org/project/dash/) - `dash`")
                        ], className="mb-4")
                    ])
                ])
            ], className="p-3")
        ], id="tabs", active_tab="tab-1", className="mb-4")
    ], fluid=True, className="py-4")

@callback(
    [Output("user-email-current", "children"),
     Output("user-name-current", "children"),
     Output("user-user-current", "children"),
     Output("user-ip-current", "children"),
     Output("all-headers-current", "children")],
    Input("tabs", "active_tab"),
)
def update_user_info(tab):
    headers = dict(request.headers)
    
    # Get specific user details from headers
    email = headers.get("X-Forwarded-Email", 'Not available')
    username = headers.get("X-Forwarded-Preferred-Username", 'Not available')
    user  = headers.get("X-Forwarded-User", 'Not available')
    ip = headers.get("X-Real-Ip", 'Not available')
    
    # Format all headers for display
    all_headers = "\n".join([f"{k}: {v}" for k, v in headers.items()])
    
    return email, username, user, ip, all_headers

# Make layout available at module level
__all__ = ['layout']
