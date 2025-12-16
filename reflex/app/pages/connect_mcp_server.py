import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app import theme


def _pattern_accordion(title: str, description: str, code: str) -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            rx.accordion.header(
                rx.accordion.trigger(
                    rx.hstack(
                        rx.text(title, class_name="font-medium"),
                        rx.icon("chevron-down", class_name="h-4 w-4"),
                        justify="between",
                        width="100%",
                        align="center",
                    ),
                    class_name="flex items-center w-full px-4 py-2 text-sm font-semibold rounded-lg transition-colors",
                    color="white",
                    background_color="#3B82F6",
                    _hover={
                        "background_color": theme.ACTIVE_ITEM_BG,
                        "color": theme.ACTIVE_ITEM_TEXT,
                    },
                )
            ),
            rx.accordion.content(
                rx.vstack(
                    rx.text(description, class_name="font-semibold text-gray-700 mb-2"),
                    rx.code_block(code, language="python", width="100%"),
                    spacing="2",
                    width="100%",
                    padding="4",
                )
            ),
            value="item-1",
            style={
                "background_color": "white",
                "border": "1px solid #E5E7EB",
                "border_radius": "0.5rem",
            },
        ),
        type="single",
        collapsible=True,
        width="100%",
        class_name="mb-2",
    )


def connect_mcp_code_display() -> rx.Component:
    return rx.vstack(
        _pattern_accordion(
            "OAuth User to Machine Per User (On-behalf-of-user)",
            "Pattern 1: OAuth User to Machine Per User (On-behalf-of-user)",
            """
import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json

token = st.context.headers.get("x-forwarded-access-token")
w = WorkspaceClient(token=token, auth_type="pat")

def init_mcp_session(w: WorkspaceClient, connection_name: str):
    init_payload = {
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {}
    }
    response = w.serving_endpoints.http_request(
        conn=connection_name,
        method=ExternalFunctionRequestHttpMethod.POST,
        path="/",
        json=init_payload,
    )
    return response.headers.get("mcp-session-id")

class McpState(rx.State):
    response_data: str = ""

    async def send_request(self):
        connection_name = "github_u2m_connection"
        http_method = ExternalFunctionRequestHttpMethod.POST
        path = "/"
        headers = {"Content-Type": "application/json"}
        payload = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}

        session_id = init_mcp_session(w, connection_name)
        headers["Mcp-Session-Id"] = session_id

        response = w.serving_endpoints.http_request(
            conn=connection_name,
            method=http_method,
            path=path,
            headers=headers,
            json=payload,
        )
        self.response_data = response.json()
""",
        ),
        _pattern_accordion(
            "Bearer token",
            "Pattern 2: Bearer token",
            """
import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

w = WorkspaceClient()

response = w.serving_endpoints.http_request(
    conn="github_u2m_connection",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/",
    headers={"Accept": "application/vnd.github+json"},
    json={
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {}
    },
)

rx.code_block(response.json(), language="json")
""",
        ),
        width="100%",
        spacing="4",
    )


from app.states.connect_mcp_server_state import ConnectMcpServerState


def connect_mcp_server_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
* `USE CONNECTION` on the Unity Catalog HTTP Connection.
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
            rx.markdown(
                """
* [Unity Catalog HTTP Connection](https://docs.databricks.com/en/connectors/http-api.html)
""",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* [databricks-sdk](https://pypi.org/project/databricks-sdk/)
* [reflex](https://pypi.org/project/reflex/)
* [mcp[cli]](https://pypi.org/project/mcp/)
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


def connect_mcp_server_content() -> rx.Component:
    """Content for the 'Try It' tab of the Connect MCP Server page."""
    return rx.vstack(
        rx.box(
            rx.vstack(
                rx.icon("info", class_name="h-5 w-5 text-blue-600"),
                rx.text(
                    "This sample will only work as intended when deployed to Databricks Apps and not when running locally. Also, you need to configure on-behalf-of-user authentication for this Databricks Apps application.",
                    class_name="text-sm text-blue-800",
                ),
                spacing="2",
            ),
            class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg w-full mb-4",
        ),
        rx.vstack(
            rx.text("Connection Name", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="github_mcp_oauth",
                on_change=ConnectMcpServerState.set_connection_name,
                class_name="w-full",
                default_value=ConnectMcpServerState.connection_name,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Auth Mode", class_name="font-semibold text-sm"),
            rx.select(
                [
                    "OAuth User to Machine Per User (On-behalf-of-user)",
                    "Bearer token",
                    "OAuth Machine to Machine",
                ],
                value=ConnectMcpServerState.auth_mode,
                on_change=ConnectMcpServerState.set_auth_mode,
                width="100%",
            ),
            width="100%",
        ),
        rx.hstack(
            rx.vstack(
                rx.text("HTTP Method", class_name="font-semibold text-sm"),
                rx.select(
                    ["POST", "GET", "PUT", "DELETE", "PATCH"],
                    value=ConnectMcpServerState.http_method,
                    on_change=ConnectMcpServerState.set_http_method,
                    class_name="w-full",
                ),
                width="30%",
            ),
            rx.vstack(
                rx.text("Request Data (JSON)", class_name="font-semibold text-sm"),
                rx.text_area(
                    on_change=ConnectMcpServerState.set_request_data,
                    class_name="w-full h-32 font-mono text-sm",
                    default_value=ConnectMcpServerState.request_data,
                ),
                width="70%",
            ),
            width="100%",
            spacing="4",
            align="start",
        ),
        rx.button(
            "Send Request",
            on_click=ConnectMcpServerState.send_request,
            is_loading=ConnectMcpServerState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            ConnectMcpServerState.mcp_session_id,
            rx.box(
                rx.text(
                    "Active MCP Session ID:",
                    class_name="font-semibold text-xs text-green-700 uppercase",
                ),
                rx.text(
                    ConnectMcpServerState.mcp_session_id,
                    class_name="font-mono text-sm text-green-900",
                ),
                class_name="p-2 bg-green-50 border border-green-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            ConnectMcpServerState.error_message,
            rx.vstack(
                rx.box(
                    rx.hstack(
                        rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                        rx.text(ConnectMcpServerState.error_message, color="red.500"),
                    ),
                    class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
                ),
                rx.cond(
                    ConnectMcpServerState.login_url,
                    rx.link(
                        "Authenticate with Connection Provider",
                        href=ConnectMcpServerState.login_url,
                        is_external=True,
                        class_name="text-blue-600 underline font-semibold mt-2 block",
                    ),
                ),
                width="100%",
            ),
        ),
        rx.cond(
            ConnectMcpServerState.response_data,
            rx.vstack(
                rx.text("Response", class_name="font-semibold text-sm"),
                rx.code_block(
                    ConnectMcpServerState.response_data,
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def connect_mcp_server_page() -> rx.Component:
    """The Connect an MCP Server sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Connect an MCP Server",
            page_description="Establish and verify a connection to a multi-cluster-proxy (MCP) server.",
            try_it_content=connect_mcp_server_content,
            code_snippet_content=connect_mcp_code_display,
            requirements_content=connect_mcp_server_requirements,
        )
    )