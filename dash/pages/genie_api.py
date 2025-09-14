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
            data = get_query_result(response.query_result.statement_id)
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
    )
    return table


def format_message_display(chat_history: List[Dict]) -> List[Dict]:
    formatted_messages = []
    for message in chat_history:
        if message["role"] == "user":
            formatted_messages.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("You", className="text-primary mb-2"),
                        html.P(message["content"], className="mb-0")
                    ])
                ], className="mb-3")
            )
        else:
            formatted_messages.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Genie", className="text-success mb-2"),
                        html.P(message["content"], className="mb-0")
                    ])
                ], className="mb-3")
            )
    return formatted_messages


def get_query_result(statement_id: str) -> dash.dash_table.DataTable:     
    try:
        result = w.statement_execution.get_statement(statement_id)
        df = pd.DataFrame(
            result.result.data_array, 
            columns=[i.name for i in result.manifest.schema.columns]
        )
        return dash_dataframe(df)
    except Exception as e:
        return html.Div(f"Error loading data: {str(e)}", className="text-danger")


def process_genie_response(response: GenieMessage, chat_history: List[Dict]) -> List[Dict]:
    for attachment in response.attachments:
        if attachment.text:
            chat_history.append({
                "role": "assistant",
                "content": attachment.text.content
            })
        elif attachment.query:
            data_table = get_query_result(response.query_result.statement_id)
            chat_history.append({
                "role": "assistant",
                "content": f"Query: {attachment.query.description}\nGenerated SQL: {attachment.query.query}",
                "data": data_table
            })
    return chat_history


def layout():
    return dbc.Container([
        # Header section matching Streamlit style
        dbc.Row([
            dbc.Col([
                html.H1("Business Intelligence", className="mb-1"),
                html.Hr(className="mb-2"),
                html.H2("Genie", className="mb-2"),
        html.P([
                    "Converse with your data. This app uses ",
            html.A(
                        "Genie API",
                        href="https://docs.databricks.com/en/ai/genie/index.html",
                        target="_blank",
                        className="text-primary"
            ),
            " to let users ask questions about your data for instant insights."
                ], className="mb-3")
            ])
        ]),
        
        # Tabbed layout
        dbc.Tabs([
            # Try it tab
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Genie Space ID:", className="form-label"),
                                dcc.Input(
                        id="genie-space-id",
                        type="text",
                                    placeholder="Enter your Genie space ID",
                                    className="form-control mb-2"
                                )
                            ], md=6),
                            dbc.Col([
                                html.Label("Conversation ID:", className="form-label"),
                                dcc.Input(
                                    id="conversation-id",
                                    type="text",
                                    placeholder="Will be generated automatically",
                                    className="form-control mb-2",
                                    readOnly=True
                                )
                            ], md=6)
                        ]),
                        html.Label("Your question:", className="form-label"),
                        dcc.Textarea(
                            id="prompt",
                            placeholder="Ask a question about your data...",
                            className="form-control mb-2",
                            rows=3
                        ),
                        dbc.Row([
                            dbc.Col([
                        dbc.Button(
                                    "Ask Genie",
                            id="chat-button",
                            color="primary",
                                    className="mb-2"
                                )
                            ], md=6),
                            dbc.Col([
                                dbc.Button(
                                    "Clear Chat",
                                    id="clear-button",
                                    color="secondary",
                                    className="mb-2"
                                )
                            ], md=6)
                        ]),
                        html.Div(id="chat-history", className="mt-3")
                    ])
                ])
            ], label="Try it", tab_id="tab-try"),
            
            # Code snippet tab
            dbc.Tab([
                dcc.Markdown(code_snippet, className="mb-0")
            ], label="Code snippet", tab_id="tab-code"),
            
            # Requirements tab
            dbc.Tab([
                dbc.Row([
                    dbc.Col(md=4, children=[
                        html.H5("Permissions", className="mb-2"),
                        html.Ul([
                            html.Li("Genie space access"),
                            html.Li("Data access permissions")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Databricks Resources", className="mb-2"),
                        html.Ul([
                            html.Li("Genie space"),
                            html.Li("SQL warehouse"),
                            html.Li("Data tables")
                        ])
                    ]),
                    dbc.Col(md=4, children=[
                        html.H5("Dependencies", className="mb-2"),
                        html.Ul([
                            html.Li("databricks-sdk"),
                            html.Li("pandas"),
                            html.Li("dash")
                        ])
                    ])
                ])
            ], label="Requirements", tab_id="tab-requirements")
        ], id="tabs", active_tab="tab-try"),
        
        # Hidden store for chat history
        dcc.Store(id="chat-history-store", data=[])
    ], fluid=True)


# Callbacks handle interactions

@callback(
    [Output("chat-history-store", "data", allow_duplicate=True),
     Output("chat-history", "children", allow_duplicate=True),
     Output("conversation-id", "value", allow_duplicate=True)],
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
     Output("conversation-id", "value", allow_duplicate=True)],
    [Input("clear-button", "n_clicks"),
     Input("genie-space-id", "value")],
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
