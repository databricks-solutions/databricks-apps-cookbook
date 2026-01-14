import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.components.loading_spinner import loading_spinner
from app.states.genie_state import GenieState
from app import theme

CODE_SNIPPET = """
import reflex as rx
from databricks.sdk import WorkspaceClient
import pandas as pd

w = WorkspaceClient()

genie_space_id = "01f0023d28a71e599b5a62f4117916d4"


def display_message(message):
    if "content" in message:
        rx.markdown(message["content"])
    if "data" in message:
        rx.data_table(message["data"])
    if "code" in message:
        rx.accordion.root(
            rx.accordion.item(
                rx.accordion.header(
                    rx.accordion.trigger("Show generated code")
                ),
                rx.accordion.content(
                    rx.code_block(message["code"], language="sql")
                ),
                value="item-1",
            ),
            type="single",
            collapsible=True,
        )


def get_query_result(statement_id):
    # For simplicity, let's say data fits in one chunk, query.manifest.total_chunk_count = 1
    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array, columns=[i.name for i in result.manifest.schema.columns]
    )


def process_genie_response(response):
    for i in response.attachments:
        if i.text:
            message = {"role": "assistant", "content": i.text.content}
            display_message(message)
        elif i.query:
            data = get_query_result(response.query_result.statement_id)
            message = {
                "role": "assistant", "content": i.query.description, "data": data, "code": i.query.query
            }
            display_message(message)


class GenieState(rx.State):
    conversation_id: str = ""
    prompt: str = ""

    @rx.event
    async def send_message(self):
        if self.prompt:
            user_prompt = self.prompt
            self.prompt = ""
            # Display user message
            # Then process with assistant
            if self.conversation_id:
                conversation = w.genie.create_message_and_wait(
                    genie_space_id, self.conversation_id, user_prompt
                )
                process_genie_response(conversation)
            else:
                conversation = w.genie.start_conversation_and_wait(genie_space_id, user_prompt)
                self.conversation_id = conversation.conversation_id
                process_genie_response(conversation)
"""


def render_chat_message(message: dict) -> rx.Component:
    """Renders a single chat message based on its role and type."""
    return rx.box(
        rx.cond(
            message["role"] == "user",
            rx.box(
                rx.text(message["content"], class_name="text-white"),
                class_name="bg-blue-600 p-3 rounded-lg ml-auto max-w-[80%] mb-2 w-fit",
            ),
            rx.box(
                rx.cond(
                    message["type"] == "text",
                    rx.markdown(message["content"], class_name="text-sm"),
                ),
                rx.cond(
                    message["type"] == "code",
                    rx.accordion.root(
                        rx.accordion.item(
                            rx.accordion.header(
                                rx.accordion.trigger(
                                    "Show SQL Query", class_name="text-sm font-semibold"
                                )
                            ),
                            rx.accordion.content(
                                rx.code_block(
                                    message["content"],
                                    language="sql",
                                    class_name="mt-2 rounded-md overflow-x-auto",
                                )
                            ),
                            value="item-1",
                        ),
                        type="single",
                        collapsible=True,
                        class_name="w-full border rounded-md bg-white",
                    ),
                ),
                rx.cond(
                    message["type"] == "data",
                    rx.box(
                        rx.text(
                            "Query Result",
                            class_name="text-xs font-semibold text-gray-500 mb-1",
                        ),
                        rx.data_table(
                            data=message["content"],
                            width="100%",
                            pagination=True,
                            search=True,
                            sort=True,
                            class_name="border rounded-md overflow-auto bg-white max-h-[60vh]",
                        ),
                        class_name="mt-2 w-full",
                    ),
                ),
                class_name="bg-gray-100 p-4 rounded-lg mr-auto max-w-[90%] mb-2 w-full overflow-hidden",
            ),
        ),
        width="100%",
    )


def genie_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
* `SELECT` on the data
* `CAN USE` on the SQL Warehouse
* `CAN VIEW` on the Genie Space
""",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Databricks resources",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown("* Genie API", class_name="text-sm text-gray-600"),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* `reflex`
* `databricks-sdk`
* `pandas`
""",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def genie_content() -> rx.Component:
    """Content for the 'Try It' tab of the Genie page."""
    return rx.vstack(
        rx.vstack(
            rx.text("Genie Space ID", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="0123456789abcdef...",
                on_change=GenieState.set_genie_space_id,
                class_name="w-full",
                default_value=GenieState.genie_space_id,
            ),
            rx.text(
                "Find the Space ID in the URL of your Genie space: /genie/spaces/<space-id>/...",
                class_name="text-xs text-gray-500",
            ),
            width="100%",
            spacing="1",
        ),
        rx.box(
            rx.vstack(
                rx.foreach(GenieState.messages, render_chat_message),
                rx.cond(GenieState.is_loading, loading_spinner("Genie is thinking...")),
                align="start",
                width="100%",
                spacing="2",
            ),
            class_name="flex-1 w-full bg-white border rounded-lg p-4 h-[500px] overflow-y-auto mb-4 shadow-sm",
        ),
        rx.hstack(
            rx.input(
                placeholder="Ask a question...",
                on_change=GenieState.set_input_text,
                class_name="flex-1",
                on_key_down=GenieState.handle_key_down,
                value=GenieState.input_text,
            ),
            rx.button(
                rx.icon("send", class_name="h-4 w-4"),
                on_click=GenieState.send_message,
                is_loading=GenieState.is_loading,
                bg=theme.PRIMARY_COLOR,
                class_name="text-white",
            ),
            width="100%",
            spacing="2",
        ),
        rx.hstack(
            rx.cond(
                GenieState.conversation_id,
                rx.button(
                    "New Chat",
                    on_click=GenieState.reset_conversation,
                    variant="outline",
                    size="2",
                ),
            ),
            rx.cond(
                GenieState.conversation_id,
                rx.link(
                    rx.button("Open Genie", variant="outline", size="2"),
                    href=GenieState.open_genie_url,
                    is_external=True,
                ),
            ),
            spacing="2",
            class_name="mt-2",
        ),
        rx.cond(
            GenieState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(GenieState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def genie_page() -> rx.Component:
    """The Genie sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Integrate with Genie",
            page_description="Explore patterns for integrating the Databricks Genie experience within your Reflex application.",
            try_it_content=genie_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=genie_requirements,
        )
    )