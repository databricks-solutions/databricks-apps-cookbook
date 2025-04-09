from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from databricks.sdk import WorkspaceClient
import dash

# pages/ml_vector_search.py
dash.register_page(
    __name__,
    path='/ml/vector-search',
    title='Run vector search',
    name='Run vector search',
    category='AI / ML',
    icon='material-symbols:search'
)

w = WorkspaceClient()

try:
    openai_client = w.serving_endpoints.get_open_ai_client()
except Exception:
    openai_client = None

EMBEDDING_MODEL_ENDPOINT_NAME = "databricks-gte-large-en"

def get_embeddings(text):
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_ENDPOINT_NAME, input=text
        )
        return response.data[0].embedding
    except Exception as e:
        return f"Error generating embeddings: {e}"

def run_vector_search(prompt: str, index_name: str, columns: str) -> str:
    prompt_vector = get_embeddings(prompt)
    if prompt_vector is None or isinstance(prompt_vector, str):
        return f"Failed to generate embeddings: {prompt_vector}"

    columns_to_fetch = [col.strip() for col in columns.split(",") if col.strip()]

    try:
        query_result = w.vector_search_indexes.query_index(
            index_name=index_name,
            columns=columns_to_fetch,
            query_vector=prompt_vector,
            num_results=3,
        )
        return query_result.result.data_array
    except Exception as e:
        return f"Error during vector search: {e}"

def layout():
    return dbc.Container([
        html.H1("AI / ML", className="my-4"),
        html.H2("Run vector search", className="mb-3"),
        html.P(
            "This recipe uses vector search for fast and accurate retrieval of the most similar items or content.",
            className="mb-4"
        ),
        
        dbc.Tabs([
            # Try it tab
            dbc.Tab([
                dbc.Form([
                    dbc.Label("Vector search index:", className="mt-3"),
                    dbc.Input(
                        id="index-name-input",
                        type="text",
                        placeholder="catalog.schema.index-name",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    
                    dbc.Label("Columns to retrieve (comma-separated):", className="mt-3"),
                    dbc.Input(
                        id="columns-input",
                        type="text",
                        placeholder="url, name",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    
                    dbc.Label("Your query:", className="mt-3"),
                    dbc.Input(
                        id="search-query-input",
                        type="text",
                        placeholder="What is Databricks?",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    
                    dbc.Button(
                        "Run vector search",
                        id="search-button",
                        color="primary",
                        className="mt-3"
                    ),
                ]),
                dbc.Spinner(
                    html.Div(id="search-results", className="mt-4"),
                    color="primary",
                    type="border",
                    fullscreen=False,
                )
            ], label="Try it", tab_id="tab-1"),
            
            # Code snippet tab
            dbc.Tab([
                dcc.Markdown('''
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
openai_client = w.serving_endpoints.get_open_ai_client()

EMBEDDING_MODEL_ENDPOINT_NAME = "databricks-gte-large-en"

def get_embeddings(text):
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_ENDPOINT_NAME, input=text
        )
        return response.data[0].embedding
    except Exception as e:
        return f"Error generating embeddings: {e}"

def run_vector_search(prompt: str) -> str:
    prompt_vector = get_embeddings(prompt)
    if prompt_vector is None or isinstance(prompt_vector, str):
        return f"Failed to generate embeddings: {prompt_vector}"

    columns_to_fetch = [col.strip() for col in columns.split(",") if col.strip()]

    try:
        query_result = w.vector_search_indexes.query_index(
            index_name=index_name,
            columns=columns_to_fetch,
            query_vector=prompt_vector,
            num_results=3,
        )
        return query_result.result.data_array
    except Exception as e:
        return f"Error during vector search: {e}"
```
                ''',className="border rounded p-3")
            ], label="Code snippet", tab_id="tab-2"),
            
            # Requirements tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions (app service principal)", className="mb-3"),
                        html.Ul([
                            dcc.Markdown("**```USE CATALOG```** on the Catalog that contains the Vector Search index"),
                            dcc.Markdown("**```USE SCHEMA```** on the Schema that contains the Vector Search index"),
                            dcc.Markdown("**```SELECT```** on the Vector Search index")
                        ], className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.Ul([
                            html.Li("Vector Search endpoint"),
                            html.Li("Vector Search index")
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
    Output("search-results", "children"),
    [Input("search-button", "n_clicks")],
    [State("index-name-input", "value"),
     State("columns-input", "value"),
     State("search-query-input", "value")],
    prevent_initial_call=True
)
def update_results(n_clicks, index_name, columns, query):
    if not all([index_name, columns, query]):
        return dbc.Alert("Please fill in all fields", color="warning")
    
    try:
        results = run_vector_search(query, index_name, columns)
        return dbc.Card(dbc.CardBody([
            html.H5("Search Results:", className="mb-3"),
            html.Pre(str(results))
        ]))
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger")

# Make layout available at module level
__all__ = ['layout']
