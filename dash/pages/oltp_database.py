import uuid
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd

from databricks.sdk import WorkspaceClient

import psycopg
from psycopg_pool import ConnectionPool

dash.register_page(__name__, path="/oltp-database", name="OLTP Database", category="Tables")

w = WorkspaceClient()


def generate_token(instance_name: str) -> str:
    cred = w.database.generate_database_credential(
        request_id=str(uuid.uuid4()), instance_names=[instance_name]
    )
    return cred.token


class RotatingTokenConnection(psycopg.Connection):
    """psycopg3 Connection that injects a fresh OAuth token as the password."""

    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        instance_name = kwargs.pop("_instance_name")
        kwargs["password"] = generate_token(instance_name)
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)


def build_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    conninfo = f"host={host} dbname={database} user={user}"
    return ConnectionPool(
        conninfo=conninfo,
        connection_class=RotatingTokenConnection,
        kwargs={"_instance_name": instance_name},
        min_size=1,
        max_size=10,
        open=True,
    )





def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if not cur.description:
                return pd.DataFrame()
            
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=cols)


def layout():
    try:
        instance_names = [i.name for i in w.database.list_database_instances()]
    except Exception:
        instance_names = []

    return dbc.Container([
        # Header
        html.Div([
            html.H1("OLTP Database", className="mb-1", style={"color": "#1f2937", "fontWeight": "600"}),
            html.Hr(style={"margin": "8px 0 24px 0", "borderColor": "#e5e7eb"}),
            html.H2("Connect a table", className="mb-3", style={"color": "#374151", "fontSize": "1.25rem", "fontWeight": "500"}),
                         html.P([
                 "This recipe connects to a ",
                 html.A("Databricks Lakebase", 
                        href="https://docs.databricks.com/aws/en/oltp/", 
                        target="_blank",
                        style={"color": "#2563eb", "textDecoration": "none"}),
                 " OLTP database instance to read data from PostgreSQL tables. "
                 "Provide the instance name, database, schema, and table to query."
             ], style={"color": "#6b7280", "marginBottom": "2rem"})
        ]),

        # Tabs
        dbc.Tabs([
            dbc.Tab(label="Try it", tab_id="try-it", label_style={"fontWeight": "500"}),
            dbc.Tab(label="Code snippet", tab_id="code", label_style={"fontWeight": "500"}),
            dbc.Tab(label="Requirements", tab_id="requirements", label_style={"fontWeight": "500"})
        ], id="tabs", active_tab="try-it", style={"marginBottom": "2rem"}),

        # Tab content
        html.Div(id="tab-content")
    ], fluid=True, className="py-4")


@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    try:
        instance_names = [i.name for i in w.database.list_database_instances()]
    except Exception:
        instance_names = []

    if active_tab == "try-it":
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Database instance:", className="form-label fw-semibold"),
                        dcc.Dropdown(
                            id="instance-dropdown",
                            options=[{"label": name, "value": name} for name in instance_names],
                            placeholder="Select a database instance",
                            style={"marginBottom": "1rem"}
                        ),
                    ], md=6),
                    dbc.Col([
                        html.Label("Database:", className="form-label fw-semibold"),
                        dbc.Input(
                            id="database-input",
                            type="text",
                            value="databricks_postgres",
                            style={"marginBottom": "1rem"}
                        ),
                    ], md=6),
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Label("Schema:", className="form-label fw-semibold"),
                        dbc.Input(
                            id="schema-input",
                            type="text",
                            value="public",
                            style={"marginBottom": "1rem"}
                        ),
                    ], md=6),
                    dbc.Col([
                        html.Label("Table:", className="form-label fw-semibold"),
                        dbc.Input(
                            id="table-input",
                            type="text",
                            value="app_state",
                            style={"marginBottom": "1rem"}
                        ),
                    ], md=6),
                ]),
                dbc.Row([
                    dbc.Col([
                                                 dbc.Button(
                             "Query Table", 
                             id="run-query-btn", 
                             color="primary",
                             size="lg",
                             className="px-4",
                             style={"marginTop": "1rem"}
                         ),
                    ], width="auto"),
                ]),
                html.Div(id="query-results", style={"marginTop": "2rem"}),
                html.Div(id="error-message")
            ])
        ], className="shadow-sm")

    elif active_tab == "code":
        return dbc.Card([
            dbc.CardBody([
                dcc.Markdown("""
```python
import uuid
import pandas as pd
from databricks.sdk import WorkspaceClient
import psycopg
from psycopg_pool import ConnectionPool

w = WorkspaceClient()

class RotatingTokenConnection(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        kwargs["password"] = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()),
            instance_names=[kwargs.pop("_instance_name")]
        ).token
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)

def build_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    return ConnectionPool(
        conninfo=f"host={host} dbname={database} user={user}",
        connection_class=RotatingTokenConnection,
        kwargs={"_instance_name": instance_name},
        min_size=1,
        max_size=5,
        open=True,
    )

def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description is None:
                return pd.DataFrame()
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)

instance_name = "dbase_instance"
database = "databricks_postgres"
schema = "public"
table = "app_state"
user = w.current_user.me().user_name
host = w.database.get_database_instance(name=instance_name).read_write_dns

pool = build_pool(instance_name, host, user, database)

# Query existing data
df = query_df(pool, f"SELECT * FROM {schema}.{table} LIMIT 10")
```
                """, 
                style={
                    "backgroundColor": "#f8f9fa", 
                    "padding": "1.5rem", 
                    "borderRadius": "0.5rem",
                    "border": "1px solid #e9ecef"
                })
            ])
        ], className="shadow-sm")

    elif active_tab == "requirements":
        return dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5("Permissions (app service principal)", className="mb-3 text-primary"),
                        html.Ul([
                            html.Li([
                                "The database instance should be specified in your ",
                                html.A("App resources", 
                                       href="https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                "."
                            ], className="mb-2"),
                            html.Li([
                                "A PostgreSQL role for the service principal is required. See ",
                                html.A("this guide", 
                                       href="https://docs.databricks.com/aws/en/oltp/pg-roles?language=PostgreSQL#create-postgres-roles-and-grant-privileges-for-databricks-identities", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                "."
                            ], className="mb-2"),
                            html.Li("The PostgreSQL service principal role should have these example grants:", className="mb-2")
                        ], className="mb-3"),
                        dcc.Markdown("""
```sql
GRANT CONNECT ON DATABASE databricks_postgres TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
GRANT USAGE, CREATE ON SCHEMA public TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_state TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
```
                        """, style={
                            "backgroundColor": "#f8f9fa", 
                            "padding": "1rem", 
                            "borderRadius": "0.375rem",
                            "fontSize": "0.875rem"
                        }),
                        html.Small([
                            html.A("This guide", 
                                   href="https://learn.microsoft.com/en-us/azure/databricks/oltp/query/sql-editor#create-a-new-query", 
                                   target="_blank",
                                   style={"color": "#6b7280"}),
                            " shows you how to query your Lakebase."
                        ], className="text-muted")
                    ], md=4),

                    dbc.Col([
                        html.H5("Databricks resources", className="mb-3 text-primary"),
                        html.Ul([
                            html.Li([
                                html.A("Lakebase", 
                                       href="https://docs.databricks.com/aws/en/oltp/", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                " database instance (PostgreSQL)."
                            ], className="mb-2"),
                            html.Li("Target PostgreSQL database/schema/table.", className="mb-2")
                        ])
                    ], md=4),

                    dbc.Col([
                        html.H5("Dependencies", className="mb-3 text-primary"),
                        html.Ul([
                            html.Li([
                                html.A("Databricks SDK", 
                                       href="https://pypi.org/project/databricks-sdk/", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                " - databricks-sdk>=0.60.0"
                            ], className="mb-2"),
                            html.Li([
                                html.A("psycopg[binary]", 
                                       href="https://pypi.org/project/psycopg/", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                ", ",
                                html.A("psycopg-pool", 
                                       href="https://pypi.org/project/psycopg-pool/", 
                                       target="_blank",
                                       style={"color": "#2563eb"})
                            ], className="mb-2"),
                            html.Li([
                                html.A("Pandas", 
                                       href="https://pypi.org/project/pandas/", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                " - pandas"
                            ], className="mb-2"),
                            html.Li([
                                html.A("Dash", 
                                       href="https://pypi.org/project/dash/", 
                                       target="_blank",
                                       style={"color": "#2563eb"}),
                                " - dash"
                            ], className="mb-2")
                        ])
                    ], md=4),
                ]),
                dbc.Alert(
                    "Tokens expire periodically; this app refreshes on each new connection and enforces TLS (sslmode=require).",
                    color="info",
                    className="mt-4"
                )
            ])
        ], className="shadow-sm")


@callback(
    [Output("query-results", "children"),
     Output("error-message", "children")],
    [Input("run-query-btn", "n_clicks")],
    [State("instance-dropdown", "value"),
     State("database-input", "value"),
     State("schema-input", "value"),
     State("table-input", "value")]
)
def run_query(n_clicks, instance_name, database, schema, table):
    if not n_clicks:
        return "", ""
    
    if not all([instance_name, database, schema, table]):
        return "", dbc.Alert("Please provide instance, database, schema, and table.", color="warning")
    
    try:
        user = w.current_user.me().user_name
        host = w.database.get_database_instance(name=instance_name).read_write_dns
        
        pool = build_pool(instance_name, host, user, database)

        # Query the data
        df = query_df(pool, f"SELECT * FROM {schema}.{table} LIMIT 10")
        
        if df.empty:
            return dbc.Alert("No data found.", color="info"), ""
        
        return dbc.Card([
            dbc.CardHeader([
                html.H5("Query Results", className="mb-0")
            ]),
            dbc.CardBody([
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    style_cell={
                        'textAlign': 'left',
                        'fontFamily': 'system-ui, -apple-system, sans-serif',
                        'fontSize': '14px',
                        'padding': '12px'
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': '600',
                        'color': '#495057',
                        'border': '1px solid #dee2e6'
                    },
                    style_data={
                        'backgroundColor': 'white',
                        'border': '1px solid #dee2e6'
                    },
                    style_table={'overflowX': 'auto'}
                )
            ])
        ], className="shadow-sm"), ""
        
    except Exception as e:
        return "", dbc.Alert(f"Error: {str(e)}", color="danger")
