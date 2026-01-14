import reflex as rx
import json
import re
import logging
from typing import Optional
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod


def get_client_obo(headers) -> WorkspaceClient:
    """
    Returns a WorkspaceClient configured for On-Behalf-Of (OBO) authentication.
    It attempts to retrieve the 'x-forwarded-access-token' from the request headers.
    """
    token = getattr(headers, "x_forwarded_access_token", "")
    host = getattr(headers, "x_forwarded_host", "")
    return WorkspaceClient(host=host, token=token, auth_type="pat")


def init_mcp_session(headers, connection_name: str) -> Optional[str]:
    """Initializes an MCP session and returns the session ID."""
    w = get_client_obo(headers)
    init_payload = {
        "jsonrpc": "2.0",
        "id": "init-auto",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "reflex-cookbook", "version": "1.0"},
        },
    }
    response = w.serving_endpoints.http_request(
        conn=connection_name,
        method=ExternalFunctionRequestHttpMethod.POST,
        path="/",
        json=init_payload,
    )
    if hasattr(response, "headers") and response.headers:
        return response.headers.get("mcp-session-id") or response.headers.get(
            "Mcp-Session-Id"
        )
    return None


def is_connection_login_error(error_msg: str) -> bool:
    """Checks if the error message indicates a need to login to the external service."""
    return (
        "consent to the required permissions" in error_msg
        or "login" in error_msg.lower()
    )


def extract_login_url_from_error(error_msg: str) -> str:
    """Extracts the login URL from the error message if present."""
    url_pattern = "(https?://[^\\s]+)"
    match = re.search(url_pattern, error_msg)
    if match:
        return match.group(1)
    return ""


class ConnectMcpServerState(rx.State):
    """State for Connect MCP Server page."""

    connection_name: str = "github_mcp_oauth"
    auth_mode: str = "OAuth User to Machine Per User (On-behalf-of-user)"
    http_method: str = "POST"
    request_data: str = """{
    "jsonrpc": "2.0",
    "id": "list-1",
    "method": "tools/list"
}"""
    mcp_session_id: str = ""
    response_data: str = ""
    login_url: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    def set_connection_name(self, value: str):
        self.connection_name = value

    @rx.event
    def set_auth_mode(self, value: str):
        self.auth_mode = value

    @rx.event
    def set_http_method(self, value: str):
        self.http_method = value

    @rx.event
    def set_request_data(self, value: str):
        self.request_data = value

    @rx.event(background=True)
    async def send_request(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.response_data = ""
            self.login_url = ""
            headers = self.router.headers
        try:
            try:
                payload = json.loads(self.request_data)
            except json.JSONDecodeError as e:
                logging.exception(f"JSON Decode Error: {e}")
                async with self:
                    self.error_message = "Invalid JSON in Request Data."
                    self.is_loading = False
                return
            w = None
            if self.auth_mode == "OAuth User to Machine Per User (On-behalf-of-user)":
                w = get_client_obo(headers)
            else:
                w = WorkspaceClient()
            method_map = {
                "POST": ExternalFunctionRequestHttpMethod.POST,
                "GET": ExternalFunctionRequestHttpMethod.GET,
                "PUT": ExternalFunctionRequestHttpMethod.PUT,
                "DELETE": ExternalFunctionRequestHttpMethod.DELETE,
                "PATCH": ExternalFunctionRequestHttpMethod.PATCH,
            }
            req_method = method_map.get(
                self.http_method, ExternalFunctionRequestHttpMethod.POST
            )
            req_headers = {}
            if self.mcp_session_id:
                req_headers["Mcp-Session-Id"] = self.mcp_session_id
            if (
                self.auth_mode == "OAuth User to Machine Per User (On-behalf-of-user)"
                and (not self.mcp_session_id)
                and (payload.get("method") != "initialize")
            ):
                try:
                    sid = init_mcp_session(headers, self.connection_name)
                    if sid:
                        req_headers["Mcp-Session-Id"] = sid
                        async with self:
                            self.mcp_session_id = sid
                except Exception as e:
                    logging.exception(f"Auto-init failed: {e}")
            response = w.serving_endpoints.http_request(
                conn=self.connection_name,
                method=req_method,
                path="/",
                headers=req_headers,
                json=payload,
            )
            if (
                not self.mcp_session_id
                and hasattr(response, "headers")
                and response.headers
            ):
                sid = response.headers.get("mcp-session-id") or response.headers.get(
                    "Mcp-Session-Id"
                )
                if sid:
                    async with self:
                        self.mcp_session_id = sid
            resp_data = response.as_dict() if hasattr(response, "as_dict") else response
            async with self:
                self.response_data = json.dumps(resp_data, indent=2)
        except Exception as e:
            error_str = str(e)
            if is_connection_login_error(error_str):
                url = extract_login_url_from_error(error_str)
                async with self:
                    self.login_url = url
                    self.error_message = "Connection requires authentication. Please click the link below."
            else:
                logging.exception(f"MCP Request Failed: {e}")
                async with self:
                    self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False