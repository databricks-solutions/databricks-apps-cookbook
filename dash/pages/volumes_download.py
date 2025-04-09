from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
import os
import base64
import dash

# pages/volumes_download.py
dash.register_page(
    __name__,
    path='/volumes/download',
    title='Download a file',
    name='Download a file',
    category='Volumes',
    icon='material-symbols:download'
)



w = WorkspaceClient()

def layout():
    """Return the layout for this view"""
    return dbc.Container([
        # Header section
        html.H1("Volumes", className="my-4"),
        html.H2("Download a file", className="mb-3"),
        html.P([
            "This recipe downloads a file from a ",
            html.A("Unity Catalog volume", 
                  href="https://docs.databricks.com/en/volumes/index.html",
                  target="_blank",
                  className="text-primary")
        ], className="mb-4"),
        
        # Tabs
        dbc.Tabs([
            dbc.Tab(label="Try it", tab_id="try-it", children=[
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Specify a path to a file in a Unity Catalog volume:", 
                                    className="fw-bold mb-2"),
                            dbc.Input(
                                id="file-path-input",
                                type="text",
                                placeholder="/Volumes/main/marketing/raw_files/leads.csv",
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
                        "Get file",
                        id="get-file-button",
                        color="primary",
                        className="mb-4",
                        size="md"
                    )
                ], className="mt-3"),
                html.Div(id="download-area", className="mt-3"),
                html.Div(id="status-area-download", className="mt-3")
            ], className="p-3"),
            
            dbc.Tab(label="Code snippet", tab_id="code-snippet", children=[
                dcc.Markdown('''```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

download_file_path = "/Volumes/catalog/schema/volume_name/file.csv"
response = w.files.download(download_file_path)
file_data = response.contents.read()
file_name = os.path.basename(download_file_path)
```''',className="border rounded p-3")
            ], className="p-3"),
            
            dbc.Tab(label="Requirements", tab_id="requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```USE CATALOG```** on the volume's catalog"),
                            dcc.Markdown("**```USE SCHEMA```** on the volume's schema"),
                            dcc.Markdown("**```READ VOLUME```** on the volume")
                        ], className="mb-4"),
                        html.P([
                            "See ",
                            html.A("Privileges required for volume operations",
                                  href="https://docs.databricks.com/en/volumes/privileges.html#privileges-required-for-volume-operations",
                                  target="_blank"),
                            " for more information."
                        ])
                    ]),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.Ul([
                            html.Li("Unity Catalog volume")
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
        ], id="tabs", active_tab="try-it", className="mb-4")
    ], fluid=True, className="py-4")

@callback(
    [Output("download-area", "children"),
     Output("status-area-download", "children")],
    Input("get-file-button", "n_clicks"),
    State("file-path-input", "value"),
    prevent_initial_call=True
)
def handle_file_download(n_clicks, file_path):
    if not file_path:
        return None, dbc.Alert("Please specify a file path.", color="warning")
    
    try:
        resp = w.files.download(file_path)
        file_data = resp.contents.read()
        file_name = os.path.basename(file_path)
        
        # Encode file data for download
        encoded = base64.b64encode(file_data).decode()
        
        download_link = html.A(
            dbc.Button(
                "Download file",
                color="success",
                className="mt-3"
            ),
            href=f"data:application/octet-stream;base64,{encoded}",
            download=file_name
        )
        
        return download_link, dbc.Alert(f"File '{file_name}' is ready for download", 
                                      color="success")
    except Exception as e:
        return None, dbc.Alert(f"Error downloading file: {str(e)}", color="danger")

# Make layout available at module level
__all__ = ['layout']