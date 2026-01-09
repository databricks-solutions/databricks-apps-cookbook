import reflex as rx
import base64
import logging
from databricks.sdk import WorkspaceClient


def get_secret(scope: str, key: str) -> str:
    w = WorkspaceClient()
    secret_response = w.secrets.get_secret(scope=scope, key=key)
    decoded_secret = base64.b64decode(secret_response.value).decode("utf-8")
    return decoded_secret


class RetrieveASecretState(rx.State):
    """State for Retrieve A Secret page."""

    scope_name: str = ""
    secret_key: str = ""
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""

    @rx.event
    def set_scope_name(self, value: str):
        self.scope_name = value

    @rx.event
    def set_secret_key(self, value: str):
        self.secret_key = value

    @rx.event(background=True)
    async def retrieve_secret(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.success_message = ""
        try:
            secret = get_secret(self.scope_name, self.secret_key)
            async with self:
                self.success_message = (
                    "Secret retrieved! The value is securely handled in the backend."
                )
        except Exception as e:
            logging.exception(f"Error retrieving secret: {e}")
            async with self:
                self.error_message = "Secret not found or inaccessible. Please create a secret scope and key before retrieving."
        finally:
            async with self:
                self.is_loading = False