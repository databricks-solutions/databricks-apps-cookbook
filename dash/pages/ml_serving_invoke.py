from json import loads
from dash import Dash, html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from databricks.sdk.errors import DatabricksError
import dash

# pages/ml_serving_invoke.py
dash.register_page(
    __name__,
    path='/ml/serving-invoke',
    title='Invoke a model',
    name='Invoke a model',
    category='AI / ML',
    icon='material-symbols:model-training'
)

# Initialize WorkspaceClient with error handling
try:
    w = WorkspaceClient()
except Exception:
    w = None

def get_endpoints():
    """Safely get endpoints with error handling"""
    try:
        if w is not None:
            endpoints = w.serving_endpoints.list()
            return [endpoint.name for endpoint in endpoints]
    except DatabricksError:
        pass
    return []

# Complete model examples table
MODEL_EXAMPLES = [
    {
        "type": "Traditional Models (e.g., scikit-learn, XGBoost)",
        "param": "dataframe_split",
        "description": "JSON-serialized DataFrame in split orientation.",
        "code": """```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="custom-regression-model",
    dataframe_split={
        "columns": ["feature1", "feature2"],
        "data": [[1.5, 2.5]]
    }
)
```"""
    },
    {
        "type": "Traditional Models",
        "param": "dataframe_records",
        "description": "JSON-serialized DataFrame in records orientation.",
        "code": """```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="custom-regression-model",
    dataframe_records={
        "feature1": [1.5],
        "feature2": [2.5]
    }
)
```"""
    },
    {
        "type": "TensorFlow and PyTorch Models",
        "param": "instances",
        "description": "Tensor inputs in row format.",
        "code": """```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

tensor_input = [[1.0, 2.0, 3.0]]
response = w.serving_endpoints.query(
    name="tensor-processing-model",
    instances=tensor_input,
)
```"""
    },
    {
        "type": "TensorFlow and PyTorch Models",
        "param": "inputs",
        "description": "Tensor inputs in columnar format.",
        "code": """```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

tensor_input = {
    "input1": [1.0, 2.0, 3.0],
    "input2": [4.0, 5.0, 6.0],
}
response = w.serving_endpoints.query(
    name="tensor-processing-model",
    inputs=tensor_input,
)
```"""
    },
    {
        "type": "Large Language Models (LLMs)",
        "param": "messages",
        "description": "Chat messages for LLM inference.",
        "code": """```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="llm-model",
    messages=[
        ChatMessage(role=ChatMessageRole.SYSTEM, content="You are a helpful assistant."),
        ChatMessage(role=ChatMessageRole.USER, content="Hello, how are you?")
    ],
    temperature=0.7
)
```"""
    }
]

def layout():
    return dbc.Container([
        # Header section matching Streamlit style
        dbc.Row([
            dbc.Col([
                html.H1("AI / ML", className="mb-2"),
                html.Hr(className="mb-3"),
        html.H2("Invoke a model", className="mb-3"),
        html.P([
            "This recipe invokes a model hosted on Mosaic AI Model Serving and returns the result. ",
            "Choose either a traditional ML model or a large language model (LLM)."
                ], className="mb-4")
            ])
        ]),
        
        # Tabbed layout matching Streamlit style
        dbc.Tabs([
            # Try it tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Select a model served by Model Serving", className="form-label fw-bold"),
                                        dcc.Dropdown(
                                            id="model-select",
                                            options=[{"label": endpoint, "value": endpoint} for endpoint in get_endpoints()],
                                            placeholder="Select a model...",
                                            className="mb-3"
                                        )
                                    ], md=8),
                    dbc.Col([
                                        html.Label("Model type", className="form-label fw-bold"),
                                        dcc.RadioItems(
                            id="model-type",
                            options=[
                                                {"label": "LLM", "value": "llm"},
                                                {"label": "Traditional ML", "value": "ml"}
                            ],
                                            value="llm",
                            className="mb-3"
                        )
                                    ], md=4)
                ]),
                html.Div(id="model-inputs"),
                html.Div(id="model-output", className="mt-3")
                            ])
                        ])
                    ])
                ])
            ], label="Try it", tab_id="tab-try"),
            
            # Code snippets tab
            dbc.Tab([
                html.H4("Model Examples", className="mb-2"),
                *[html.Div([
                    html.H5(example["type"], className="mb-1"),
                    html.P(f"Parameter: {example['param']}", className="text-muted mb-1"),
                    html.P(example["description"], className="text-muted mb-1"),
                    dcc.Markdown(example["code"], className="mb-2")
                ]) for example in MODEL_EXAMPLES]
            ], label="Code snippets", tab_id="tab-code"),
            
            # Requirements tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col(md=4, children=[
                        html.H5("Permissions", className="mb-3"),
                        html.Ul([
                            html.Li("Model serving endpoint access"),
                            html.Li("Workspace authentication")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Databricks Resources", className="mb-3"),
                        html.Ul([
                            html.Li("Model serving endpoint"),
                            html.Li("Registered model in Unity Catalog")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Dependencies", className="mb-3"),
                        html.Ul([
                            html.Li("databricks-sdk"),
                            html.Li("dash")
                        ])
                    ])
                ])
            ], label="Requirements", tab_id="tab-requirements")
        ], id="tabs", active_tab="tab-try")
    ], fluid=True)

@callback(
    Output("model-inputs", "children"),
    Input("model-type", "value")
)
def update_model_inputs(model_type):
    if model_type == "llm":
        return html.Div([
            dbc.Label("Temperature", className="fw-bold mb-2"),
            dcc.Slider(
                id="temperature-slider",
                min=0,
                max=2,
                step=0.1,
                value=1.0,
                marks={i: str(i) for i in range(3)},
                tooltip={"placement": "bottom", "always_visible": True},
                className="mb-3"
            ),
            dbc.Label("Enter your prompt:", className="fw-bold mb-2"),
            dbc.Textarea(
                id="prompt-input",
                placeholder="Ask something...",
                className="mb-3",
                style={
                    "backgroundColor": "#f8f9fa",
                    "border": "1px solid #dee2e6",
                    "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                }
            ),
            dbc.Button(
                "Invoke LLM",
                id="llm-invoke-button",
                color="primary",
                className="mb-3"
            ),
            # Add spinner for model output
            dbc.Spinner(
                html.Div(id="model-output", className="mt-3"),
                color="primary",
                type="border",
                fullscreen=False,
            )
        ])
    else:
        return html.Div([
            dbc.Alert([
                "The model has to be ",
                html.A(
                    "deployed",
                    href="https://docs.databricks.com/en/machine-learning/model-serving/create-manage-serving-endpoints.html#create-an-endpoint",
                    target="_blank"
                ),
                " to Mosaic AI Model Serving. Request pattern corresponds to the model signature ",
           
                    html.A("registered in Unity Catalog",
                           href="https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html#train-and-register-unity-catalog-compatible-models",
                           target="_blank")
            ], color="info", className="mb-3"),
            dbc.Label("Enter model input:", className="fw-bold mb-2"),
            dbc.Textarea(
                id="ml-input",
                placeholder='{"feature1": [1.5], "feature2": [2.5]}',
                className="mb-3",
                style={
                    "backgroundColor": "#f8f9fa",
                    "border": "1px solid #dee2e6",
                    "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                }
            ),
            dbc.Button(
                "Invoke ML Model",
                id="ml-invoke-button",
                color="primary",
                className="mb-3"
            ),
            # Add spinner for model output
            dbc.Spinner(
                html.Div(id="model-output", className="mt-3"),
                color="primary",
                type="border",
                fullscreen=False,
            )
        ])

# Separate callback for LLM models
@callback(
    Output("model-output", "children", allow_duplicate=True),
    [Input("llm-invoke-button", "n_clicks")],
    [State("model-select", "value"),
     State("temperature-slider", "value"),
     State("prompt-input", "value")],
    prevent_initial_call=True
)
def invoke_llm_model(n_clicks, model_name, temperature, prompt):
    if not model_name:
        return dbc.Alert("Please select a model", color="warning")
    
    if not prompt:
        return dbc.Alert("Please enter a prompt", color="warning")
        
    try:
        response = w.serving_endpoints.query(
            name=model_name,
            messages=[
                ChatMessage(role=ChatMessageRole.SYSTEM, content="You are a helpful assistant."),
                ChatMessage(role=ChatMessageRole.USER, content=prompt),
            ],
            temperature=temperature
        )
        return dcc.Markdown(f"```json\n{response.as_dict()}\n```")
    except Exception as e:
        return dbc.Alert(f"Error invoking model: {str(e)}", color="danger")

# Separate callback for traditional ML models
@callback(
    Output("model-output", "children", allow_duplicate=True),
    [Input("ml-invoke-button", "n_clicks")],
    [State("model-select", "value"),
     State("ml-input", "value")],
    prevent_initial_call=True
)
def invoke_ml_model(n_clicks, model_name, ml_input):
    if not model_name:
        return dbc.Alert("Please select a model", color="warning")
    
    if not ml_input:
        return dbc.Alert("Please enter model input", color="warning")
        
    try:
        response = w.serving_endpoints.query(
            name=model_name,
            dataframe_records=loads(ml_input)
        )
        return dcc.Markdown(f"```json\n{response.as_dict()}\n```")
    except Exception as e:
        return dbc.Alert(f"Error invoking model: {str(e)}", color="danger")

# Make layout available at module level
__all__ = ['layout']
