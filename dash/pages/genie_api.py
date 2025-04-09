from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieMessage
import pandas as pd
from typing import Dict, List


dash.register_page(
    __name__,
    path="/bi/genie",
    title="Genie",
    name="Genie",
    category="Business Intelligence",
    icon="material-symbols:chat"
)

# Initialize WorkspaceClient with error handling
try:
    w = WorkspaceClient()
except Exception:
    w = None

code_snippet = '''```python
import pandas as pd
from databricks.sdk import WorkspaceClient


# Refer to the source code for the full implmenetation.


def get_query_result(statement_id):
    # For simplicity, let's say data fits in one chunk, query.manifest.total_chunk_count = 1

    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array, columns=[i.name for i in result.manifest.schema.columns]
    )


def process_genie_response(response):
    for i in response.attachments:
        if i.text:
            print(f"A: {i.text.content}")
        elif i.query:
            data = get_query_result(i.query.statement_id)
            print(f"A: {i.query.description}")
            print(f"Data: {data}")
            print(f"Generated code: {i.query.query}")

                             
# Configuration
w = WorkspaceClient()
genie_space_id = "01f0023d28a71e599b5a62f4117516d4"

prompt = "Ask a question..."
follow_up_prompt = "Ask a follow-up..."

# Start the conversation          
conversation = w.genie.start_conversation_and_wait(genie_space_id, prompt)
process_genie_response(conversation)

# Continue the conversation
follow_up_conversation = w.genie.create_message_and_wait(
    genie_space_id, conversation.conversation_id, follow_up_prompt
)
process_genie_response(follow_up_conversation)
```'''


def dash_dataframe(df: pd.DataFrame) -> dash.dash_table.DataTable:
    table = dash.dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_table={
            "overflowX": "auto",
            "minWidth": "100%",
        },
        style_header={
            "backgroundColor": "#f8f9fa",
            "fontWeight": "bold",
            "border": "1px solid #dee2e6",
            "padding": "12px 15px"
        },
        style_cell={
            "padding": "12px 15px",
            "textAlign": "left",
            "border": "1px solid #dee2e6",
            "maxWidth": "200px",
            "overflow": "hidden",
            "textOverflow": "ellipsis"
        },
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
        },
        page_size=10,
        page_action="native",
        sort_action="native",
        sort_mode="multi"
    )

    return table


def format_message_display(chat_history: List[Dict]) -> List[Dict]:
    chat_display = []
    for message in chat_history:
        display = []
        if "content" in message:
            role = "You: " if message["role"] == "user" else f"{message['role'].capitalize()}: "
            display.append(dcc.Markdown(f"{role} {message['content']}"))
        if "data" in message:
            display.append(message["data"])
        if "code" in message:
            display.append(dcc.Markdown(f"```sql {message['code']}```", className="border rounded p-3"))
        chat_display.append(html.Div(display, style={"borderBottom": "2px solid rgba(0, 0, 0, 0.2)", "margin": "5px 0 0 0"}))

    return chat_display


def get_query_result(statement_id: str) -> dash.dash_table.DataTable:     
    query = w.statement_execution.get_statement(statement_id)
    result = query.result.data_array

    next_chunk = query.result.next_chunk_index
    while next_chunk:
        chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, next_chunk)
        result.append(chunk.data_array)
        next_chunk = chunk.next_chunk_index

    df = pd.DataFrame(result, columns=[i.name for i in query.manifest.schema.columns])

    return dash_dataframe(df)


def process_genie_response(response: GenieMessage, chat_history: List[Dict]) -> List[Dict]:
    for i in response.attachments:
        if i.text:
            message = {"role": "assistant", "content": i.text.content}
            chat_history.append(message)

        elif i.query:
            data = get_query_result(i.query.statement_id)
            message = {
                "role": "assistant", "content": i.query.description, "data": data, "code": i.query.query
            }
            chat_history.append(message)
    
    return chat_history


def layout():
    return dbc.Container([
        html.H1("Genie", className="my-4"),
        html.H2("Converse with your data", className="mb-3"),
        html.P([
            "This app uses ",
            html.A(
                "Genie",
                href="https://www.databricks.com/product/ai-bi",
                target="_blank"
            ),
            " ",
            html.A(
                "API",
                href="https://docs.databricks.com/api/workspace/genie",
                target="_blank"
            ),
            " to let users ask questions about your data for instant insights."
        ], className="mb-4"),
        
        dbc.Tabs([
            # Try it tab
            dbc.Tab(label="Try it", children=[
                dbc.Form([
                    dbc.Label("Genie Space ID:", className="mt-3"),
                    dbc.Input(
                        id="genie-space-id",
                        type="text",
                        placeholder="01efe16a65e21836acefb797ae6a8fe4",
                        style={
                            "backgroundColor": "#f8f9fa",
                            "border": "1px solid #dee2e6",
                            "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)"
                        }
                    ),
                    dbc.InputGroup([
                        dbc.Input(
                            id="prompt",
                            type="text",
                            placeholder="Ask your question...",
                            style={
                                "backgroundColor": "#f8f9fa",
                                "border": "1px solid #dee2e6",
                                "boxShadow": "inset 0 1px 2px rgba(0,0,0,0.075)",
                                "margin": "5px 0 0 0",
                            }
                        ),
                        dbc.Button(
                            "Chat",
                            id="chat-button",
                            color="primary",
                            style={
                                "margin": "5px 0 0 0",
                            }
                        )
                    ])
                ], className="mb-4"),
                
                # Chat history area
                html.Div(id="chat-history", className="mt-4"),
                dcc.Store(id="chat-history-store"),
                dcc.Store(id="conversation-id"),
                dbc.Button("New Chat", id="clear-button", n_clicks=0, className="mt-3"),
                dbc.Button("Open Genie", id="genie-button", target="_blank", href="", style={"display": "none"}, className="mt-3"),

            ], className="p-3"),
            
            # Code snippet tab
            dbc.Tab(label="Code snippet", children=[
                dcc.Markdown(code_snippet, className="p-4 border rounded")
            ], className="p-3"),
            
            # Requirements tab
            dbc.Tab(label="Requirements", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("Permissions", className="mb-3"),
                        html.Ul([
                            html.Li("Unity Catalog table"),
                            html.Li("SQL warehouse"),
                            html.Li("Genie Space"),
                        ], className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Databricks resources", className="mb-3"),
                        html.Ul([
                            html.Li("Genie API")
                        ], className="mb-4")
                    ]),
                    dbc.Col([
                        html.H4("Dependencies", className="mb-3"),
                        html.Ul([
                            html.Li(["Databricks SDK - ", html.Code("databricks-sdk")]),
                            html.Li(["Pandas - ", html.Code("pandas")]),
                            html.Li(["Dash - ", html.Code("dash")])
                        ], className="mb-4")
                    ])
                ])
            ], className="p-3")
        ], className="mb-4")
    ], fluid=True, className="py-4")


# Callbacks handle interactions

@callback(
    [Output("chat-history-store", "data", allow_duplicate=True),
     Output("chat-history", "children", allow_duplicate=True),
     Output("conversation-id", "value", allow_duplicate=True),],
     Input("chat-button", "n_clicks"),
    [State("genie-space-id", "value"),
     State("conversation-id", "value"),
     State("prompt", "value"),
     State("chat-history-store", "data")],
    prevent_initial_call=True,
)
def update_chat(n_clicks, genie_space_id, conversation_id, prompt, chat_history):
    if not all([genie_space_id, prompt]):
        return dash.no_update, dbc.Alert("Please fill in all fields", color="warning")

    chat_history = chat_history or []
    chat_history.append({"role": "user", "content": prompt})

    try:
        if conversation_id:
            conversation = w.genie.create_message_and_wait(genie_space_id, conversation_id, prompt)
            # Access error codes via conversation.error for detailed exception handling.
        else:
            conversation = w.genie.start_conversation_and_wait(genie_space_id, prompt)
            conversation_id = conversation.conversation_id
            # Access error codes via conversation.error for detailed exception handling.

        chat_history = process_genie_response(conversation, chat_history)
        chat_display = format_message_display(chat_history)

        return chat_history, chat_display, conversation_id

    except Exception as e:
        return dash.no_update, dbc.Alert(f"Check the required permissions. An error occurred: {str(e)}", color="danger"), ""


@callback(
    [Output("chat-history-store", "data", allow_duplicate=True),
     Output("chat-history", "children", allow_duplicate=True),
     Output("conversation-id", "value", allow_duplicate=True),],
    [Input("clear-button", "n_clicks"),
     Input("genie-space-id", "value"),],
     prevent_initial_call=True,
)
def clear_chat(n_clicks, value):
    return [], [], None if n_clicks or value else (dash.no_update, dash.no_update, None)


@callback(
    [Output("genie-button", "href"), Output("genie-button", "style")],
    State("genie-space-id", "value"),
    Input("conversation-id", "value"),
)
def update_href(genie_space_id, conversation_id):
    if not conversation_id:
        return "", {"display": "none"}

    href = f"{w.config.host}/genie/rooms/{genie_space_id}/chats/{conversation_id}"

    return href, {"margin": "0 0 0 5px"}


# Make layout available at module level
__all__ = ["layout"]
