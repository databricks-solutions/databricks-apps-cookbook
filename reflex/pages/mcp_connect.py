import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json

class State(rx.State):
    response: str = ""
    connection_name: str = "github_u2m_connection"

    def run_mcp_list(self):
        w = WorkspaceClient()
        init_payload = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {}
        }
        init_resp = w.serving_endpoints.http_request(
            conn=self.connection_name,
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            json=init_payload,
        )
        session_id = init_resp.headers.get("mcp-session-id")

        headers = {"Content-Type": "application/json"}
        if session_id:
            headers["Mcp-Session-Id"] = session_id

        payload = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}

        resp = w.serving_endpoints.http_request(
            conn=self.connection_name,
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            headers=headers,
            json=payload,
        )

        try:
            self.response = json.dumps(resp.json(), indent=2)
        except Exception:
            self.response = resp.text or ""

def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Connect an MCP server (Reflex)"),
        rx.button("Run", on_click=State.run_mcp_list),
        rx.box(rx.text(State.response), padding="4", width="100%", white_space="pre"),
        spacing="4",
        padding="4"
    )
