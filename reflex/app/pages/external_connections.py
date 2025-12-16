import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.external_connections_state import ExternalConnectionsState
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


def external_connections_code_display() -> rx.Component:
    return rx.vstack(
        _pattern_accordion(
            "OAuth User to Machine Per User (On-behalf-of-user)",
            "Pattern 1: OAuth User to Machine Per User (On-behalf-of-user)",
            """
import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json

def init_mcp_session(w: WorkspaceClient, connection_name: str):
    init_payload = {
        "jsonrpc": "2.0",
        "id": "init-1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "reflex-cookbook", "version": "1.0"},
        }
    }
    response = w.serving_endpoints.http_request(
        conn=connection_name,
        method=ExternalFunctionRequestHttpMethod.POST,
        path="/",
        json=init_payload,
    )
    return response.headers.get("mcp-session-id")

class ExternalConnectionsState(rx.State):
    response_data: str = ""

    @rx.event
    async def run(self):
        # 1. Get token from headers
        headers = self.router.headers
        token = getattr(headers, "x_forwarded_access_token", "")

        # 2. Initialize WorkspaceClient with the token
        w = WorkspaceClient(token=token, auth_type="pat")

        # 3. Initialize Session
        connection_name = "github_mcp_oauth"
        session_id = init_mcp_session(w, connection_name)

        # 4. Make request with session ID
        headers = {"Mcp-Session-Id": session_id}
        payload = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}

        response = w.serving_endpoints.http_request(
            conn=connection_name,
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            headers=headers,
            json=payload,
        )
        self.response_data = json.dumps(response.as_dict(), indent=2)
""",
        ),
        _pattern_accordion(
            "Bearer token",
            "Pattern 2: Bearer token",
            """
import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json

class ExternalConnectionsState(rx.State):
    response_data: str = ""

    @rx.event
    async def run(self):
        # 1. Initialize WorkspaceClient (uses environment or default auth)
        w = WorkspaceClient()

        # 2. Direct HTTP GET request
        response = w.serving_endpoints.http_request(
            conn="github_u2m_connection",
            method=ExternalFunctionRequestHttpMethod.GET,
            path="/",
            headers={"Accept": "application/vnd.github+json"},
        )

        self.response_data = json.dumps(response.as_dict(), indent=2)
""",
        ),
        width="100%",
        spacing="4",
    )


def external_connections_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* `USE CONNECTION` permission on the HTTP Connection.
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
* `databricks-sdk`
* `reflex`
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


def external_connections_content() -> rx.Component:
    """Content for the 'Try It' tab of the External Connections page."""
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
            rx.text(
                "Unity Catalog Connection name:", class_name="font-semibold text-sm"
            ),
            rx.input(
                placeholder="Enter connection name...",
                on_change=ExternalConnectionsState.set_connection_name,
                class_name="w-full",
                default_value=ExternalConnectionsState.connection_name,
            ),
            rx.link(
                "Learn more about Connections",
                href="https://docs.databricks.com/en/connectors/http-api.html",
                is_external=True,
                class_name="text-xs text-blue-600 hover:underline",
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
                value=ExternalConnectionsState.auth_mode,
                on_change=ExternalConnectionsState.set_auth_mode,
                width="100%",
            ),
            width="100%",
        ),
        rx.hstack(
            rx.vstack(
                rx.text("HTTP Method", class_name="font-semibold text-sm"),
                rx.select(
                    ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    value=ExternalConnectionsState.http_method,
                    on_change=ExternalConnectionsState.set_http_method,
                    class_name="w-full",
                ),
                width="25%",
            ),
            rx.vstack(
                rx.text("Path", class_name="font-semibold text-sm"),
                rx.input(
                    placeholder="/api/endpoint",
                    on_change=ExternalConnectionsState.set_path,
                    class_name="w-full",
                    default_value=ExternalConnectionsState.path,
                ),
                width="75%",
            ),
            width="100%",
            spacing="4",
            align="start",
        ),
        rx.vstack(
            rx.text("Request headers (JSON):", class_name="font-semibold text-sm"),
            rx.text_area(
                placeholder='{"Content-Type": "application/json"}',
                on_change=ExternalConnectionsState.set_request_headers,
                class_name="w-full h-24 font-mono text-sm",
                default_value=ExternalConnectionsState.request_headers,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Request data (JSON):", class_name="font-semibold text-sm"),
            rx.text_area(
                placeholder='{"key": "value"}',
                on_change=ExternalConnectionsState.set_request_data,
                class_name="w-full h-32 font-mono text-sm",
                default_value=ExternalConnectionsState.request_data,
            ),
            width="100%",
        ),
        rx.button(
            "Send Request",
            on_click=ExternalConnectionsState.send_request,
            is_loading=ExternalConnectionsState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            ExternalConnectionsState.error_message,
            rx.box(
                rx.hstack(
                    rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                    rx.text(ExternalConnectionsState.error_message, color="red.500"),
                ),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            ExternalConnectionsState.response_data,
            rx.vstack(
                rx.text("Response", class_name="font-semibold text-sm"),
                rx.code_block(
                    ExternalConnectionsState.response_data,
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


def external_connections_page() -> rx.Component:
    """The External Connections sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="External Connections",
            page_description="Manage and view external data source connections within your Databricks environment.",
            try_it_content=external_connections_content,
            code_snippet_content=external_connections_code_display,
            requirements_content=external_connections_requirements,
        )
    )