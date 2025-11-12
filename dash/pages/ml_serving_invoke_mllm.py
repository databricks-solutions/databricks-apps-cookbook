from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import base64
import io
from PIL import Image
from typing import Dict, List
from databricks.sdk import WorkspaceClient
import dash

# Register this as a page if using multi-page Dash app structure
dash.register_page(
    __name__,
    path="/ml/multimodal",
    title="Invoke a multi-modal LLM",
    name="Invoke a multi-modal LLM",
    category="AI / ML",
    icon="material-symbols:image"
)

# Initialize WorkspaceClient
try:
    w = WorkspaceClient()
    model_client = w.serving_endpoints.get_open_ai_client()
except Exception:
    w = None
    model_client = None


def pillow_image_to_base64_string(image):
    """Convert a Pillow image to a base64-encoded string for API transmission."""
    buffered = io.BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def chat_with_mllm(endpoint_name, prompt, image, messages=None) -> tuple[str, Dict]:
    """
    Chat with a multi-modal LLM using Mosaic AI Model Serving.
    
    This function sends the prompt and image(s) to, e.g., a Claude Sonnet 3.7 endpoint
    using Databricks SDK.
    """
    image_data = pillow_image_to_base64_string(image)
    messages = messages or []

    current_user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                },
            },
        ],
    }
    messages.append(current_user_message)

    completion = model_client.chat.completions.create(
        model=endpoint_name,
        messages=messages,
    )
    completion_text = completion.choices[0].message.content

    messages.append({
        "role": "assistant",
        "content": [{
            "type": "text",
            "text": completion_text
        }]
    })

    return completion_text, messages

code_snippet = '''
import io
import base64
from PIL import Image
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
model_client = w.serving_endpoints.get_open_ai_client()


def pillow_image_to_base64_string(image):
    buffered = io.BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def chat_with_mllm(endpoint_name, prompt, image):
    image_data = pillow_image_to_base64_string(image)
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ],
    }]
    completion = model_client.chat.completions.create(
        model=endpoint_name,
        messages=messages,
    )

    return completion.choices[0].message.content
'''

def layout():
    # Get model endpoint names if client is available
    endpoint_names = []
    if w:
        try:
            endpoints = w.serving_endpoints.list()
            endpoint_names = [endpoint.name for endpoint in endpoints]
        except:
            endpoint_names = ["Error loading endpoints"]
    
    return dbc.Container([
        html.H1("AI / ML", className="my-4"),
        html.H2("Invoke a multi-modal LLM", className="mb-3"),
        html.P([
            "Upload an image and provide a prompt for multi-modal inference, e.g., with ",
            html.A("Claude Sonnet 3.7", 
                  href="https://www.databricks.com/blog/anthropic-claude-37-sonnet-now-natively-available-databricks",
                  target="_blank"),
            "."
        ], className="mb-4"),
        
        dbc.Tabs([
            # Try it tab
            dbc.Tab(label="Try it", children=[
                dbc.Row([
                    dbc.Col([
                        html.Label("Select a multi-modal Model Serving endpoint"),
                        dcc.Dropdown(
                            id="model-dropdown",
                            options=[{"label": name, "value": name} for name in endpoint_names],
                            value=endpoint_names[0] if endpoint_names else None,
                            className="mb-3"
                        ),
                        
                        html.Label("Select an image (JPG, JPEG, or PNG)"),
                        dcc.Upload(
                            id="upload-image",
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Select a File')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            multiple=False,
                            accept='image/*'
                        ),
                        
                        html.Label("Enter your prompt:"),
                        dcc.Textarea(
                            id="prompt-input",
                            placeholder="Describe or ask something about the image...",
                            value="Describe the image(s) as an alternative text",
                            style={'width': '100%', 'height': 100},
                            className="mb-3"
                        ),
                        
                        dbc.Button("Invoke LLM", id="invoke-button", color="primary", className="mb-3"),
                        
                        # Store for the uploaded image
                        dcc.Store(id="uploaded-image-store"),
                    ], width=6),
                    
                    dbc.Col([
                        html.Div(id="image-preview", className="mb-3"),
                        html.Div(id="llm-response", className="p-3 border rounded")
                    ], width=6)
                ])
            ], className="p-3"),
            
            # Code snippet tab
            dbc.Tab(label="Code snippet", children=[
                dcc.Markdown(f"```python\n{code_snippet}\n```", className="p-4 border rounded")
            ], className="p-3"),
            
            # Requirements tab
            dbc.Tab(label="Requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            html.Li("`CAN QUERY` on the model serving endpoint")
                        ], className="mb-4")
                    ], width=4),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.Ul([
                            html.Li("Multi-modal Model Serving endpoint")
                        ], className="mb-4")
                    ], width=4),
                    dbc.Col([
                        html.H4("Dependencies", className="mb-3"),
                        html.Ul([
                            html.Li([
                                html.A("Databricks SDK for Python", href="https://pypi.org/project/databricks-sdk/", target="_blank"),
                                " - ",
                                html.Code("databricks-sdk")
                            ]),
                            html.Li([
                                html.A("Dash", href="https://pypi.org/project/dash/", target="_blank"),
                                " - ",
                                html.Code("dash")
                            ])
                        ], className="mb-4")
                    ], width=4)
                ])
            ], className="p-3")
        ], className="mb-4")
    ], fluid=True, className="py-4")

@callback(
    [Output("image-preview", "children"),
     Output("uploaded-image-store", "data")],
    Input("upload-image", "contents"),
    State("upload-image", "filename"),
    prevent_initial_call=True
)
def update_image_preview(contents, filename):
    if contents is None:
        return html.Div("No image uploaded"), None
    
    # Parse the content
    content_type, content_string = contents.split(',')
    
    # Display the image
    preview = html.Div([
        html.H5("Uploaded image"),
        html.Img(src=contents, style={'maxWidth': '100%', 'maxHeight': '400px'}),
        html.P(filename)
    ])
    
    return preview, contents

@callback(
    Output("llm-response", "children"),
    [Input("invoke-button", "n_clicks")],
    [State("model-dropdown", "value"),
     State("prompt-input", "value"),
     State("uploaded-image-store", "data")],
    prevent_initial_call=True
)
def invoke_llm(n_clicks, model, prompt, image_data):
    if not all([model, prompt, image_data]):
        return dbc.Alert("Please select a model, enter a prompt, and upload an image", color="warning")
    
    try:
        # Process the base64 image
        content_type, content_string = image_data.split(',')
        decoded = base64.b64decode(content_string)
        image = Image.open(io.BytesIO(decoded))
        
        # Call the LLM
        completion_text, _ = chat_with_mllm(
            endpoint_name=model,
            prompt=prompt,
            image=image
        )
        
        return html.Div([
            html.H5("LLM Response:"),
            dcc.Markdown(completion_text)
        ])
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Make layout available at module level for page registration
__all__ = ["layout"]

# If running as standalone app
if __name__ == '__main__':
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = layout()
    app.run_server(debug=True)