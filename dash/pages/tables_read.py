import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd
from functools import lru_cache
import logging

# pages/tables_read.py
dash.register_page(
    __name__,
    path='/tables/read',
    title='Read Table',
    name='Read a table',
    category='Tables',
    icon='table'
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cfg = Config()

@lru_cache(maxsize=1)
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

layout = dbc.Container([
    html.H1("Tables", className="my-4"),
    html.H2("Read a table", className="mb-3"),
    html.P([
        "This recipe reads a Unity Catalog table using the ",
        html.A("Databricks SQL Connector", 
              href="https://docs.databricks.com/en/dev-tools/python-sql-connector.html",
              target="_blank",
              className="text-primary")
    ], className="mb-4"),
    
    dbc.Tabs([
        dbc.Tab(label="Try it", tab_id="try-it", children=[
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Enter your Databricks HTTP Path:", className="fw-bold mb-2"),
                        dbc.Input(
                            id="http-path-input",
                            type="text",
                            placeholder="/sql/1.0/warehouses/xxxxxx",
                            className="mb-3",
                            style={
                                "backgroundColor": "#f8f9fa",
                                "border": "1px solid #dee2e6",
                                "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                            }
                        )
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Specify a Unity Catalog table name:", className="fw-bold mb-2"),
                        dbc.Input(
                            id="table-name-input",
                            type="text",
                            placeholder="catalog.schema.table",
                            className="mb-3",
                            style={
                                "backgroundColor": "#f8f9fa",
                                "border": "1px solid #dee2e6",
                                "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                            }
                        )
                    ], width=12)
                ]),
                dbc.Button(
                    "Load Table",
                    id="load-button-read",
                    color="primary",
                    className="mb-4",
                    size="md"
                )
            ], className="mt-3"),
            dbc.Spinner(
                html.Div(id="table-area-read", className="mt-3"),
                color="primary",
                type="border",
                fullscreen=False,
            ),
            html.Div(id="status-area-read", className="mt-3")
        ], className="p-3"),
        
        dbc.Tab(label="Code snippet", tab_id="code-snippet", children=[
            dcc.Markdown('''```python
from databricks import sql
from databricks.sdk.core import Config
from functools import lru_cache

cfg = Config()  # Set the DATABRICKS_HOST environment variable when running locally

@lru_cache(maxsize=1)
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

http_path_input = "/sql/1.0/warehouses/xxxxxx"
table_name = "catalog.schema.table"
conn = get_connection(http_path_input)
df = read_table(table_name, conn)
```''',className="border rounded p-3")
        ], className="p-3"),
        
        dbc.Tab(label="Requirements", tab_id="requirements", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Permissions (app service principal)", className="mb-3"),
                    html.Ul([
                        dcc.Markdown("**```SELECT```** on the Unity Catalog table"),
                        dcc.Markdown("**```CAN USE```** on the SQL warehouse")
                    ], className="mb-4")
                ]),
                dbc.Col([
                    html.H4("Databricks resources", className="mb-3"),
                    html.Ul([
                        html.Li("SQL warehouse"),
                        html.Li("Unity Catalog table")
                    ], className="mb-4")
                ]),
                dbc.Col([
                    html.H4("Dependencies", className="mb-3"),
                    html.Ul([
                        dcc.Markdown("* [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`"),
                        dcc.Markdown("* [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector`"),
                        dcc.Markdown("* [Dash](https://pypi.org/project/dash/) - `dash`")
                    ], className="mb-4")
                ])
            ])
        ], className="p-3")
    ], id="tabs", active_tab="try-it", className="mb-4")
], fluid=True, className="py-4")

@callback(
    [Output("table-area-read", "children"),
     Output("status-area-read", "children")],
    Input("load-button-read", "n_clicks"),
    [State("http-path-input", "value"),
     State("table-name-input", "value")],
    prevent_initial_call=True,
    loading_state={'type': 'default', 'component_name': 'table-load'}
)
def load_table_data_read(n_clicks, http_path, table_name):
    print(f"Input values: http_path={http_path}, table_name={table_name}")  # Debug print
    
    if not http_path or not table_name:
        return None, dbc.Alert("Please provide both HTTP path and table name", color="warning")
    
    try:
        conn = get_connection(http_path)
        
        df = read_table(table_name, conn)
        
        
        if df.empty:
            return None, dbc.Alert("The query returned no data", color="warning")
            
        table = dash.dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={
                'overflowX': 'auto',
                'minWidth': '100%',
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #dee2e6',
                'padding': '12px 15px'
            },
            style_cell={
                'padding': '12px 15px',
                'textAlign': 'left',
                'border': '1px solid #dee2e6',
                'maxWidth': '200px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
    
            page_size=10,
            page_action='native',
            sort_action='native',
            sort_mode='multi'
        )
        return table, dbc.Alert("Table loaded successfully!", color="success", dismissable=True)
    except Exception as e:
        print(f"Error in callback: {str(e)}")  # Debug print
        return None, dbc.Alert(f"Error loading table: {str(e)}", color="danger")

# Make layout available at module level
__all__ = ['layout']
