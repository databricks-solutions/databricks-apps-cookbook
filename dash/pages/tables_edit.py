from dash import Dash, html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd
from functools import lru_cache
import dash

# pages/tables_edit.py
dash.register_page(
    __name__,
    path='/tables/edit',
    title='Edit Table',
    name='Edit a table',
    category='Tables',
    icon='table'
)

cfg = Config()

@lru_cache(maxsize=1)
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
    with conn.cursor() as cursor:
        rows = list(df.itertuples(index=False))
        values = ",".join([f"({','.join(map(repr, row))})" for row in rows])
        cursor.execute(f"INSERT OVERWRITE {table_name} VALUES {values}")

def layout():
    return dbc.Container([
        html.H1("Tables", className="my-4"),
        html.H2("Edit a table", className="mb-3"),
        html.P([
            "Use this recipe to read, edit, and write back data stored in a small Unity Catalog table with ",
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
                            dbc.Label("Specify the HTTP Path to your Databricks SQL Warehouse:", className="fw-bold mb-2"),
                            dbc.Input(id="http-path-input", type="text", placeholder="/sql/1.0/warehouses/xxxxxx", className="mb-3",
                                      style={
                                          "backgroundColor": "#f8f9fa",
                                          "border": "1px solid #dee2e6",
                                          "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                                      })
                        ], width=12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Specify a Catalog table name:", className="fw-bold mb-2"),
                            dbc.Input(id="table-name-input", type="text", placeholder="catalog.schema.table", className="mb-3",
                                      style={
                                          "backgroundColor": "#f8f9fa",
                                          "border": "1px solid #dee2e6",
                                          "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                                      })
                        ], width=12)
                    ]),
                    dbc.Button("Load Table", id="load-button-edit", color="primary", className="mb-4", size="md")
                ], className="mt-3"),
                dbc.Spinner(
                    html.Div(id="table-editor", className="mt-3"),
                    color="primary",
                    type="border",
                    fullscreen=False,
                ),
                dbc.Button("Save Changes", id="save-button-edit", color="success", className="mt-3 d-none", size="md"),
                html.Div(id="status-area-edit", className="mt-3")
            ], className="p-3"),
            
            dbc.Tab(label="Code snippet", tab_id="code-snippet", children=[
                dcc.Markdown('''```python
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd
from functools import lru_cache

cfg = Config()
                             
@lru_cache(maxsize=1)
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
    with conn.cursor() as cursor:
        rows = list(df.itertuples(index=False))
        values = ",".join([f"({','.join(map(repr, row))})" for row in rows])
        cursor.execute(f"INSERT OVERWRITE {table_name} VALUES {values}")

http_path_input = "/sql/1.0/warehouses/xxxxxx"
table_name = "catalog.schema.table"
conn = get_connection(http_path_input)
df = read_table(table_name, conn)
# Edit the dataframe
insert_overwrite_table(table_name, df, conn)
```''',className="border rounded p-3")
            ], className="p-3"),
            
            dbc.Tab(label="Requirements", tab_id="requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```MODIFY```** on the Unity Catalog table"),
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
                            dcc.Markdown("* [Pandas](https://pypi.org/project/pandas/) - `pandas`"),
                            dcc.Markdown("* [Dash](https://pypi.org/project/dash/) - `dash`")
                        ], className="mb-4")
                    ])
                ])
            ], className="p-3")
        ], id="tabs", active_tab="try-it", className="mb-4")
    ], fluid=True, className="py-4")

@callback(
    [Output("table-editor", "children"),
     Output("save-button-edit", "className"),
     Output("status-area-edit", "children", allow_duplicate=True)],
    Input("load-button-edit", "n_clicks"),
    [State("http-path-input", "value"),
     State("table-name-input", "value")],
    prevent_initial_call=True
)
def load_table_data_edit(n_clicks, http_path, table_name):
    if not http_path or not table_name:
        return None, "mt-3 d-none", dbc.Alert("Please provide both HTTP path and table name", color="warning")
    try:
        conn = get_connection(http_path)
        df = read_table(table_name, conn)
        table = dash_table.DataTable(
            id='editing-table',
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i, 'editable': True} for i in df.columns],
            editable=True,
            row_deletable=True,
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
            sort_mode='multi',
        )
        return table, "mt-3", None
    except Exception as e:
        return None, "mt-3 d-none", dbc.Alert(f"Error loading table: {str(e)}", color="danger")

@callback(
    Output("status-area-edit", "children"),
    Input("save-button-edit", "n_clicks"),
    [State("editing-table", "data"),
     State("table-name-input", "value"),
     State("http-path-input", "value")],
    prevent_initial_call=True
)
def save_changes(n_clicks, table_data, table_name, http_path):
    if not n_clicks:
        return None
    try:
        conn = get_connection(http_path)
        df = pd.DataFrame(table_data)
        insert_overwrite_table(table_name, df, conn)
        return dbc.Alert("Changes saved successfully", color="success")
    except Exception as e:
        return dbc.Alert(f"Error saving changes: {str(e)}", color="danger")

# Make layout available at module level
__all__ = ['layout']
