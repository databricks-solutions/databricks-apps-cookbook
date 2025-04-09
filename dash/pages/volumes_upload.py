from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import SecurableType
import os
import io
import base64
import dash

# pages/volumes_upload.py
dash.register_page(
    __name__,
    path='/volumes/upload',
    title='Volumes Upload',
    name='Upload a file',
    category='Volumes',
    icon='material-symbols:upload'
)

w = WorkspaceClient()

def check_upload_permissions(volume_name: str):
    """Check if user has required permissions on the volume"""
    try:
        volume = w.volumes.read(name=volume_name)
        current_user = w.current_user.me()
        grants = w.grants.get_effective(
            securable_type=SecurableType.VOLUME,
            full_name=volume.full_name,
            principal=current_user.user_name,
        )

        if not grants or not grants.privilege_assignments:
            return "Insufficient permissions: No grants found."

        for assignment in grants.privilege_assignments:
            for privilege in assignment.privileges:
                if privilege.privilege.value in ["ALL_PRIVILEGES", "WRITE_VOLUME"]:
                    return "Volume and permissions validated"

        return "Insufficient permissions: Required privileges not found."
    except Exception as e:
        return f"Error: {e}"

def layout():
    """Return the layout for this view"""
    return dbc.Container([
        # Header section
        html.H1("Volumes", className="my-4"),
        html.H2("Upload a file", className="mb-3"),
        html.P([
            "This recipe uploads a file to a ",
            html.A("Unity Catalog Volume",
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
                            dbc.Label("Specify a Unity Catalog Volume name:", className="fw-bold mb-2"),
                            dbc.Input(
                                id="volume-path-input",
                                type="text",
                                placeholder="main.marketing.raw_files",
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
                        "Check Volume and permissions",
                        id="check-volume-button",
                        color="primary",
                        className="mb-4",
                        size="md"
                    )
                ], className="mt-3"),
                
                html.Div(id="upload-area", className="mt-3"),
                html.Div(id="status-area-upload", className="mt-3")
            ], className="p-3"),
            
            dbc.Tab(label="Code snippet", tab_id="code-snippet", children=[
                dcc.Markdown('''```python
import io
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Read file into bytes
with open("local_file.csv", "rb") as f:
    file_bytes = f.read()
binary_data = io.BytesIO(file_bytes)

# Specify volume path and upload
volume_path = "main.marketing.raw_files"
parts = volume_path.strip().split(".")
catalog = parts[0]
schema = parts[1]
volume_name = parts[2]
volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/local_file.csv"
w.files.upload(volume_file_path, binary_data, overwrite=True)
```''',className="border rounded p-3")
            ], className="p-3"),
            
            dbc.Tab(label="Requirements", tab_id="requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```USE CATALOG```** on the catalog of the volume"),
                            dcc.Markdown("**```USE SCHEMA```** on the schema of the volume"),
                            dcc.Markdown("**```READ VOLUME```** and **```WRITE VOLUME```** on the volume")
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
    [Output("upload-area", "children"),
     Output("status-area-upload", "children")],
    Input("check-volume-button", "n_clicks"),
    State("volume-path-input", "value"),
    prevent_initial_call=True
)
def handle_volume_check(n_clicks, volume_path):
    if not volume_path:
        return None, dbc.Alert("Please specify a volume path.", color="warning")
    
    permission_result = check_upload_permissions(volume_path.strip())
    if permission_result == "Volume and permissions validated":
        upload_form = dbc.Form([
            # File upload section with simple inline filename display
            html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        dbc.Button(
                            "Select file to upload",
                            color="primary",
                            className="me-2"
                        ),
                        html.Span(id="selected-filename", style={"vertical-align": "middle"})
                    ], style={"display": "inline-block"})
                )
            ], className="mb-3"),
            dbc.Button(
                f"Upload file to {volume_path}",
                id="upload-button",
                color="success",
                className="mt-3",
                disabled=True
            )
        ])
        return upload_form, dbc.Alert("Volume and permissions validated", color="success")
    else:
        return None, dbc.Alert(permission_result, color="danger")

@callback(
    Output("upload-button", "disabled"),
    Input("upload-data", "contents"),
    prevent_initial_call=True
)
def enable_upload_button(contents):
    return contents is None

@callback(
    Output("status-area-upload", "children", allow_duplicate=True),
    Input("upload-button", "n_clicks"),
    [State("upload-data", "contents"),
     State("upload-data", "filename"),
     State("volume-path-input", "value")],
    prevent_initial_call=True
)
def handle_file_upload(n_clicks, contents, filename, volume_path):
    if not contents or not filename or not volume_path:
        return dbc.Alert("Please select a file and specify a volume path.", color="warning")
    
    try:
        # Decode base64 file content
        content_type, content_string = contents.split(',')
        file_bytes = base64.b64decode(content_string)
        binary_data = io.BytesIO(file_bytes)
        
        # Parse volume path and create file path
        parts = volume_path.strip().split(".")
        volume_file_path = f"/Volumes/{parts[0]}/{parts[1]}/{parts[2]}/{filename}"
        
        # Upload file
        w.files.upload(volume_file_path, binary_data, overwrite=True)
        
        # Generate volume URL for success message
        databricks_host = os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_HOSTNAME")
        volume_url = f"https://{databricks_host}/explore/data/volumes/{parts[0]}/{parts[1]}/{parts[2]}"
        
        return dbc.Alert([
            f"File '{filename}' successfully uploaded to ",
            html.Strong(volume_path),
            ". ",
            html.A("Go to volume", href=volume_url, target="_blank")
        ], color="success")
    except Exception as e:
        return dbc.Alert(f"Error uploading file: {str(e)}", color="danger")

# Simple callback to show filename
@callback(
    Output("selected-filename", "children"),
    Input("upload-data", "filename"),
    prevent_initial_call=True
)
def update_filename(filename):
    if filename:
        return filename
    return ""

# Make layout available at module level
__all__ = ['layout']
