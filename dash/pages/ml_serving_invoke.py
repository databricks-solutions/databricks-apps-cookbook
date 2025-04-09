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
        "code": '''from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="custom-regression-model",
    dataframe_split={
        "columns": ["feature1", "feature2"],
        "data": [[1.5, 2.5]]
    }
)'''
    },
    {
        "type": "Traditional Models",
        "param": "dataframe_records",
        "description": "JSON-serialized DataFrame in records orientation.",
        "code": '''from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="custom-regression-model",
    dataframe_records={
        "feature1": [1.5],
        "feature2": [2.5]
    }
)'''
    },
    {
        "type": "TensorFlow and PyTorch Models",
        "param": "instances",
        "description": "Tensor inputs in row format.",
        "code": '''from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

tensor_input = [[1.0, 2.0, 3.0]]
response = w.serving_endpoints.query(
    name="tensor-processing-model",
    instances=tensor_input,
)'''
    },
    {
        "type": "TensorFlow and PyTorch Models",
        "param": "inputs",
        "description": "Tensor inputs in columnar format.",
        "code": '''from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

tensor_input = {
    "input1": [1.0, 2.0, 3.0],
    "input2": [4.0, 5.0, 6.0],
}
response = w.serving_endpoints.query(
    name="tensor-processing-model",
    inputs=tensor_input,
)'''
    },
    {
        "type": "Completions Models",
        "param": "prompt",
        "description": "Input text for completion tasks.",
        "code": '''from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="llm-text-completions-model",
    prompt="Generate a recipe for building scalable Databricks Apps.",
    temperature=0.5,
)'''
    },
    {
        "type": "Chat Models",
        "param": "messages",
        "description": "List of chat messages for conversational models.",
        "code": '''from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="chat-assistant-model",
    messages=[
        ChatMessage(
            role=ChatMessageRole.SYSTEM, 
            content="You are a helpful assistant.",
        ),
        ChatMessage(
            role=ChatMessageRole.USER, 
            content="Provide tips for deploying Databricks Apps.",
        ),
    ],
)'''
    },
    {
        "type": "Embeddings Models",
        "param": "input",
        "description": "Input text for embedding tasks.",
        "code": '''from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="embedding-model",
    input="Databricks provides a unified analytics platform.",
)'''
    }
]

def layout():
    endpoint_names = get_endpoints()
    
    # Create model selection interface based on authentication status
    if endpoint_names:
        model_selector = dcc.Dropdown(
            id="model-select",
            options=[{"label": name, "value": name} for name in endpoint_names],
            className="mb-3"
        )
    else:
        model_selector = html.Div([
            dbc.Alert([
                "Unable to fetch model endpoints. Please ensure you have:",
                html.Ul([
                    html.Li("Valid Databricks authentication credentials"),
                    html.Li([
                        html.A("CAN QUERY permission", 
                              href="https://docs.databricks.com/en/machine-learning/model-serving/model-serving-permissions.html",
                              target="_blank",
                              className="alert-link"),
                        " on the model serving endpoints"
                    ])
                ])
            ], color="warning", className="mb-3"),
            dcc.Input(
                id="model-select",
                type="text",
                placeholder="Enter model endpoint name manually",
                className="form-control mb-3",
                style={
                    "backgroundColor": "#f8f9fa",
                    "border": "1px solid #dee2e6",
                    "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                }
            )
        ])
    
    return dbc.Container([
        html.H1("AI / ML", className="my-4"),
        html.H2("Invoke a model", className="mb-3"),
        html.P([
            "This recipe invokes a model hosted on Mosaic AI Model Serving and returns the result. ",
            "Choose either a traditional ML model or a large language model (LLM)."
        ], className="mb-4"),
        
        dbc.Tabs([
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Select a model served by Model Serving", className="fw-bold mb-2"),
                        model_selector
                    ], width=8),
                    dbc.Col([
                        dbc.Label("Model type", className="fw-bold mb-2"),
                        dbc.RadioItems(
                            id="model-type",
                            options=[
                                {"label": "LLM", "value": "LLM"},
                                {"label": "Traditional ML", "value": "Traditional ML"}
                            ],
                            value="LLM",
                            className="mb-3"
                        )
                    ], width=4)
                ]),
                html.Div(id="model-inputs"),
                html.Div(id="model-output", className="mt-3")
            ], label="Try it", tab_id="tab-1"),
            
            dbc.Tab([
                dbc.Accordion([
                    dbc.AccordionItem(
                        [
                            html.P(example["description"]),
                            dcc.Markdown(f'''```python\n{example["code"]}\n```''')
                        ],
                        title=f"{example['type']} ({example['param']})"
                    ) for example in MODEL_EXAMPLES
                ], start_collapsed=True, className="mb-4"),
                
                html.Div([
                    html.H4("Extensions", className="mt-4 mb-3"),
                    html.Ul([
                        html.Li([
                            html.A("Gradio", href="https://www.gradio.app/", target="_blank"),
                            ": Enable ML prototyping with pre-built interactive components for models involving images, audio, or video."
                        ]),
                        html.Li([
                            html.A("Dash", href="https://dash.plotly.com/", target="_blank"),
                            ": Build interactive, data-rich visualizations to explore and analyze the behavior of your ML models in depth."
                        ]),
                        html.Li([
                            html.A("Shiny", href="https://shiny.posit.co/", target="_blank"),
                            ": Build AI chat apps."
                        ]),
                        html.Li([
                            html.A("LangChain on Databricks", href="https://python.langchain.com/docs/integrations/providers/databricks", target="_blank"),
                            ": Excels at chaining LLM calls, integration with external APIs, and managing conversational contexts."
                        ])
                    ], className="mb-3"),
                    html.P([
                        "Also, check out ",
                        html.A("Databricks Serving Query API", 
                              href="https://docs.databricks.com/api/workspace/servingendpoints/query",
                              target="_blank"),
                        ". It provides the example responses and optional arguments for the above ",
                        html.Em("Implement"),
                        " cases."
                    ])
                ], className="alert alert-info")
            ], label="Code snippets", tab_id="tab-2"),
            
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```CAN QUERY```** on the model serving endpoint")
                        ], className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.Ul([
                            html.Li("Model serving endpoint")
                        ], className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Dependencies", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("* [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`"),
                            dcc.Markdown("* [Dash](https://pypi.org/project/dash/) - `dash`")
                        ], className="mb-4")
                    ])
                ])
            ], label="Requirements", tab_id="tab-3")
        ], id="tabs", active_tab="tab-1", className="mb-4")
    ], fluid=True, className="py-4")

@callback(
    Output("model-inputs", "children"),
    Input("model-type", "value")
)
def update_model_inputs(model_type):
    if model_type == "LLM":
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
