import reflex as rx
import json
import logging
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod


def get_client_obo(headers: dict[str, str]) -> WorkspaceClient:
    token = headers.get("x-forwarded-access-token")
    host = headers.get("x-forwarded-host")
    return WorkspaceClient(host=host, token=token)


class ExternalConnectionsState(rx.State):
    """State for External Connections page."""

    connection_name: str = ""
    auth_mode: str = "OAuth User to Machine Per User (On-behalf-of-user)"
    http_method: str = "GET"
    path: str = "/"
    request_headers: str = '{"Content-Type": "application/json"}'
    request_data: str = "{}"
    response_data: str = ""
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
    def set_path(self, value: str):
        self.path = value

    @rx.event
    def set_request_headers(self, value: str):
        self.request_headers = value

    @rx.event
    def set_request_data(self, value: str):
        self.request_data = value

    @rx.event(background=True)
    async def send_request(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.response_data = ""
            if not self.connection_name or not self.path:
                self.error_message = (
                    "Please fill in all required fields (Connection Name, Path)."
                )
                self.is_loading = False
                return
            headers = self.router.headers
        try:
            try:
                req_headers_dict = (
                    json.loads(self.request_headers) if self.request_headers else {}
                )
            except json.JSONDecodeError as e:
                logging.exception(f"Invalid JSON in Request Headers: {e}")
                async with self:
                    self.error_message = "Invalid JSON in Request Headers."
                    self.is_loading = False
                return
            try:
                req_data_dict = (
                    json.loads(self.request_data) if self.request_data else {}
                )
            except json.JSONDecodeError as e:
                logging.exception(f"Invalid JSON in Request Data: {e}")
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
                "GET": ExternalFunctionRequestHttpMethod.GET,
                "POST": ExternalFunctionRequestHttpMethod.POST,
                "PUT": ExternalFunctionRequestHttpMethod.PUT,
                "DELETE": ExternalFunctionRequestHttpMethod.DELETE,
                "PATCH": ExternalFunctionRequestHttpMethod.PATCH,
            }
            req_method = method_map.get(
                self.http_method, ExternalFunctionRequestHttpMethod.GET
            )
            response = w.serving_endpoints.http_request(
                conn=self.connection_name,
                method=req_method,
                path=self.path,
                headers=req_headers_dict,
                json=req_data_dict
                if req_method != ExternalFunctionRequestHttpMethod.GET
                else None,
            )
            resp_data = response.as_dict() if hasattr(response, "as_dict") else response
            async with self:
                self.response_data = json.dumps(resp_data, indent=2)
        except Exception as e:
            logging.exception(f"External Connection Request Failed: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False