import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.retrieve_a_secret_state import RetrieveASecretState
from app import theme

CODE_SNIPPET = """
import reflex as rx
import base64
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_secret(scope, key):
    try:
        secret_response = w.secrets.get_secret(scope=scope, key=key)
        decoded_secret = base64.b64decode(secret_response.value).decode('utf-8')
        return decoded_secret
    except Exception as e:
        return None

class RetrieveASecretState(rx.State):
    scope_name: str = "my_secret_scope"
    secret_key: str = "api_key"
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""

    @rx.event(background=True)
    async def retrieve_secret(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.success_message = ""

        try:
            secret = get_secret(self.scope_name, self.secret_key)
            async with self:
                if secret:
                    self.success_message = "Secret retrieved! The value is securely handled in the backend."
                else:
                    self.error_message = "Secret not found or inaccessible. Please create a secret scope and key before retrieving."
        except Exception:
            async with self:
                self.error_message = "Secret not found or inaccessible. Please create a secret scope and key before retrieving."
        finally:
            async with self:
                self.is_loading = False
"""


def retrieve_a_secret_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                "* `CAN READ` permission on the Secret Scope",
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
* Secret Scope
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


def retrieve_a_secret_content() -> rx.Component:
    """Content for the 'Try It' tab."""
    return rx.vstack(
        rx.vstack(
            rx.text("Secret Scope", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="apis",
                on_change=RetrieveASecretState.set_scope_name,
                class_name="w-full",
                default_value=RetrieveASecretState.scope_name,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Secret Key", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="weather_service_key",
                on_change=RetrieveASecretState.set_secret_key,
                class_name="w-full",
                default_value=RetrieveASecretState.secret_key,
            ),
            width="100%",
        ),
        rx.button(
            "Retrieve",
            on_click=RetrieveASecretState.retrieve_secret,
            is_loading=RetrieveASecretState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
        ),
        rx.cond(
            RetrieveASecretState.success_message,
            rx.box(
                rx.hstack(
                    rx.icon("circle-check", class_name="text-green-500 mr-2"),
                    rx.text(RetrieveASecretState.success_message, color="green.700"),
                ),
                class_name="p-4 bg-green-50 border border-green-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            RetrieveASecretState.error_message,
            rx.box(
                rx.hstack(
                    rx.icon("triangle-alert", class_name="text-red-500 mr-2"),
                    rx.text(RetrieveASecretState.error_message, color="red.500"),
                ),
                class_name="p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def retrieve_a_secret_page() -> rx.Component:
    """The Retrieve a Secret sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Retrieve a Secret",
            page_description="Securely access secrets stored in Databricks Secrets to use them in your application's backend logic.",
            try_it_content=retrieve_a_secret_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=retrieve_a_secret_requirements,
        )
    )