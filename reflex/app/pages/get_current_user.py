import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.get_current_user_state import GetCurrentUserState
from app import theme

CODE_SNIPPET = """
import reflex as rx
from databricks.sdk import WorkspaceClient
import json
import asyncio
import logging


class GetCurrentUserState(rx.State):
    header_email: str = ""
    header_username: str = ""
    header_user: str = ""
    header_ip: str = ""
    header_token: str = ""
    user_id: str = ""
    user_name: str = ""
    user_display_name: str = ""
    user_active: bool = False
    user_external_id: str = ""
    groups_count: int = 0
    entitlements_count: int = 0
    user_json: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def get_user_headers(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            headers = self.router.headers
            # Convert HeaderData to dict safely
            try:
                headers_dict = {k: v for k, v in vars(headers).items() if not k.startswith('_')}
            except Exception:
                headers_dict = {}
            self.all_headers_json = json.dumps(headers_dict, indent=2)

            self.header_email = getattr(headers, "x_forwarded_email", "")
            self.header_username = getattr(
                headers, "x_forwarded_preferred_username", ""
            )
            self.header_user = getattr(headers, "x_forwarded_user", "")
            self.header_ip = getattr(headers, "x_real_ip", "")
            self.header_token = getattr(headers, "x_forwarded_access_token", "")
        try:
            if self.header_token:
                loop = asyncio.get_running_loop()

                def fetch_user_info(token):
                    w = WorkspaceClient(token=token, auth_type="pat")
                    return w.current_user.me()

                me = await loop.run_in_executor(
                    None, fetch_user_info, self.header_token
                )
                async with self:
                    self.user_id = me.id
                    self.user_name = me.user_name or ""
                    self.user_display_name = me.display_name or ""
                    self.user_active = me.active
                    self.user_external_id = me.external_id or ""
                    self.groups_count = len(me.groups) if me.groups else 0
                    self.entitlements_count = len(me.entitlements) if me.entitlements else 0
                    self.user_json = json.dumps(me.as_dict(), indent=2)
            else:
                async with self:
                    pass
        except Exception as e:
            logging.exception(f"Error fetching current user: {e}")
            async with self:
                self.error_message = f"Error fetching user info: {e}"
        finally:
            async with self:
                self.is_loading = False
"""


def get_current_user_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                "No permissions configuration required for accessing headers. To use the `current_user.me()` API, the app must be configured with on-behalf-of-user authentication.",
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
            rx.markdown("None", class_name="text-sm text-gray-600"),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.el.ul(
                rx.el.li(
                    rx.link(
                        "reflex",
                        href="https://pypi.org/project/reflex/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                rx.el.li(
                    rx.link(
                        "databricks-sdk",
                        href="https://pypi.org/project/databricks-sdk/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                class_name="list-disc list-inside text-sm text-gray-600 pl-2",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def get_current_user_content() -> rx.Component:
    """Content for the 'Try It' tab."""
    return rx.vstack(
        rx.button(
            "Get User Headers",
            on_click=GetCurrentUserState.get_user_headers,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white mb-4",
            is_loading=GetCurrentUserState.is_loading,
        ),
        rx.cond(
            GetCurrentUserState.is_loading,
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Loading user info...", class_name="text-gray-500"),
                align="center",
                justify="center",
                class_name="w-full h-32 bg-gray-50 rounded-lg",
            ),
            rx.vstack(
                rx.box(
                    rx.hstack(
                        rx.icon(
                            "info", class_name="h-5 w-5 text-blue-600 flex-shrink-0"
                        ),
                        rx.markdown(
                            "For this sample to work when running on your local machine, use the `databricks apps run-local` CLI command which injects the necessary HTTP headers.",
                            class_name="text-sm text-blue-800",
                        ),
                        align="start",
                        spacing="2",
                    ),
                    class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg w-full mb-4",
                ),
                rx.heading(
                    "Information extracted from HTTP headers",
                    size="4",
                    class_name="font-semibold text-gray-800 mb-2",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("E-mail:", class_name="font-semibold"),
                        rx.text(GetCurrentUserState.header_email),
                    ),
                    rx.hstack(
                        rx.text("Username:", class_name="font-semibold"),
                        rx.text(GetCurrentUserState.header_username),
                    ),
                    rx.hstack(
                        rx.text("IP Address:", class_name="font-semibold"),
                        rx.text(GetCurrentUserState.header_ip),
                    ),
                    rx.hstack(
                        rx.text(
                            "X-Forwarded-Access-Token present:",
                            class_name="font-semibold",
                        ),
                        rx.cond(
                            GetCurrentUserState.header_token,
                            rx.text("✅"),
                            rx.text("❌"),
                        ),
                    ),
                    align="start",
                    class_name="text-sm mb-4",
                    spacing="2",
                ),
                rx.accordion.root(
                    rx.accordion.item(
                        rx.accordion.header(
                            rx.accordion.trigger(
                                "All headers", class_name="font-semibold text-sm"
                            )
                        ),
                        rx.accordion.content(
                            rx.code_block(
                                GetCurrentUserState.all_headers_json,
                                language="json",
                                class_name="w-full overflow-x-auto text-xs",
                            )
                        ),
                        value="all_headers",
                    ),
                    collapsible=True,
                    type="single",
                    class_name="w-full mb-6 border rounded-md bg-white",
                ),
                rx.heading(
                    rx.link(
                        "Information extracted from w.current_user.me()",
                        href="https://databricks-sdk-py.readthedocs.io/en/latest/workspace/iam/current_user.html",
                        is_external=True,
                        class_name="text-gray-800 hover:text-blue-600",
                    ),
                    size="4",
                    class_name="font-semibold mb-2",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon(
                            "info", class_name="h-5 w-5 text-blue-600 flex-shrink-0"
                        ),
                        rx.markdown(
                            "Enable [on-behalf-of-user authentication](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development#-using-the-databricks-apps-authorization-model) for this app to see information about the user visiting the app. Otherwise, this will display information about the app service principal.",
                            class_name="text-sm text-blue-800",
                        ),
                        align="start",
                        spacing="2",
                    ),
                    class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg w-full mb-4",
                ),
                rx.cond(
                    GetCurrentUserState.header_token,
                    rx.vstack(
                        rx.hstack(
                            rx.text("User ID:", class_name="font-semibold"),
                            rx.text(GetCurrentUserState.user_id),
                        ),
                        rx.hstack(
                            rx.text("Username:", class_name="font-semibold"),
                            rx.text(GetCurrentUserState.user_name),
                        ),
                        rx.hstack(
                            rx.text("Display Name:", class_name="font-semibold"),
                            rx.text(GetCurrentUserState.user_display_name),
                        ),
                        rx.hstack(
                            rx.text("Active:", class_name="font-semibold"),
                            rx.text(GetCurrentUserState.user_active.to_string()),
                        ),
                        rx.hstack(
                            rx.text("Groups:", class_name="font-semibold"),
                            rx.text(f"{GetCurrentUserState.groups_count} groups"),
                        ),
                        rx.hstack(
                            rx.text("Entitlements:", class_name="font-semibold"),
                            rx.text(
                                f"{GetCurrentUserState.entitlements_count} entitlements"
                            ),
                        ),
                        align="start",
                        class_name="text-sm mb-4",
                        spacing="2",
                    ),
                    rx.text(
                        "No access token found. User info cannot be retrieved.",
                        class_name="text-sm text-gray-500 italic mb-4",
                    ),
                ),
                rx.cond(
                    GetCurrentUserState.user_json,
                    rx.accordion.root(
                        rx.accordion.item(
                            rx.accordion.header(
                                rx.accordion.trigger(
                                    "Full user object",
                                    class_name="font-semibold text-sm",
                                )
                            ),
                            rx.accordion.content(
                                rx.code_block(
                                    GetCurrentUserState.user_json,
                                    language="json",
                                    class_name="w-full overflow-x-auto text-xs",
                                )
                            ),
                            value="user_json",
                        ),
                        collapsible=True,
                        type="single",
                        class_name="w-full border rounded-md bg-white",
                    ),
                ),
                rx.cond(
                    GetCurrentUserState.error_message,
                    rx.box(
                        rx.hstack(
                            rx.icon("triangle-alert", class_name="text-red-500"),
                            rx.text(
                                GetCurrentUserState.error_message,
                                class_name="text-red-500",
                            ),
                        ),
                        class_name="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg w-full",
                    ),
                ),
                width="100%",
                align="start",
            ),
        ),
        width="100%",
        align="start",
    )


def get_current_user_page() -> rx.Component:
    """The Get Current User sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Get Current User",
            page_description="Identify the user currently authenticated with the Databricks workspace.",
            try_it_content=get_current_user_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=get_current_user_requirements,
        )
    )