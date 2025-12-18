import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.components.loading_spinner import loading_spinner
from app.states.ai_bi_dashboard_state import AiBiDashboardState
from app import theme

CODE_SNIPPET = """
import reflex as rx
import requests
import time
from databricks.sdk.core import Config

# 1. Helper to fetch published dashboards from Databricks API
def get_published_dashboards():
    cfg = Config()
    headers = {"Authorization": f"Bearer {cfg.token}"}
    host = cfg.host.rstrip("/")
    url = f"{host}/api/2.0/lakeview/dashboards"

    def fetch_with_retry(target_url):
        retries = 3
        delay = 1
        for attempt in range(retries + 1):
            response = requests.get(target_url, headers=headers)
            if response.status_code == 429:
                if attempt < retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
            return response
        return None

    # Fetch all dashboards
    response = fetch_with_retry(url)
    if not response: return {}
    response.raise_for_status()

    data = response.json()
    published = {}
    for d in data.get("dashboards", []):
        dash_id = d.get("dashboard_id")
        display = d.get("display_name", "Untitled")

        # Check published status individually
        pub_url = f"{host}/api/2.0/lakeview/dashboards/{dash_id}/published"
        pub_resp = fetch_with_retry(pub_url)

        if pub_resp and pub_resp.status_code == 200:
            published[display] = dash_id

    return published

class AiBiDashboardState(rx.State):
    dashboard_options: dict[str, str] = {}
    selected_dashboard: str = ""
    iframe_source: str = ""

    @rx.var
    def dashboard_names(self) -> list[str]:
        return list(self.dashboard_options.keys())

    @rx.event
    def on_load(self):
        # Fetch available dashboards on load
        self.dashboard_options = get_published_dashboards()
        if self.dashboard_options:
            # Default to the first one
            self.selected_dashboard = self.dashboard_names[0]
            self.update_src()

    @rx.event
    def set_selected_dashboard(self, value: str):
        self.selected_dashboard = value
        self.update_src()

    def update_src(self):
        # Construct the embed URL
        cfg = Config()
        host = cfg.host.rstrip("/")
        dash_id = self.dashboard_options.get(self.selected_dashboard)
        if dash_id:
            self.iframe_source = f"{host}/embed/dashboardsv3/{dash_id}"
"""


def ai_bi_dashboard_requirements() -> rx.Component:
    return rx.vstack(
        rx.grid(
            rx.vstack(
                rx.heading(
                    "Permissions (app service principal)",
                    size="4",
                    class_name="font-semibold text-gray-800",
                ),
                rx.markdown(
                    """
* `CAN VIEW` permission on the dashboard
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
                rx.markdown("* SQL Warehouse", class_name="text-sm text-gray-600"),
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
        ),
        rx.box(
            rx.hstack(
                rx.icon("triangle-alert", class_name="text-blue-600"),
                rx.text(
                    "A workspace admin needs to enable dashboard embedding in the Security settings of your Databricks workspace for specific domains (e.g., databricksapps.com) or all domains for this sample to work.",
                    class_name="text-blue-800 text-sm",
                ),
                align="center",
            ),
            class_name="p-4 bg-blue-50 border border-blue-200 rounded-lg w-full",
        ),
        spacing="4",
        width="100%",
    )


def ai_bi_dashboard_content() -> rx.Component:
    """Content for the 'Try It' tab of the AI/BI Dashboard page."""
    return rx.vstack(
        rx.text("Select a Dashboard", class_name="font-semibold text-sm"),
        rx.select(
            AiBiDashboardState.dashboard_names,
            value=AiBiDashboardState.selected_dashboard,
            on_change=AiBiDashboardState.set_selected_dashboard,
            placeholder="Select a dashboard...",
            class_name="w-full",
        ),
        rx.cond(
            AiBiDashboardState.iframe_source,
            rx.box(
                rx.el.iframe(
                    src=AiBiDashboardState.iframe_source,
                    class_name="w-full h-[800px] border rounded-lg shadow-sm bg-white",
                    allow="clipboard-write; fullscreen",
                ),
                class_name="w-full mt-4",
            ),
            rx.cond(
                AiBiDashboardState.is_loading,
                loading_spinner("Loading published dashboards..."),
                rx.box(
                    rx.text(
                        "No published dashboards found or selected.",
                        class_name="text-gray-500 italic",
                    ),
                    class_name="p-8 w-full text-center",
                ),
            ),
        ),
        rx.cond(
            AiBiDashboardState.error_message,
            rx.box(
                rx.hstack(
                    rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                    rx.text(AiBiDashboardState.error_message, color="red.500"),
                ),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def ai_bi_dashboard_page() -> rx.Component:
    """The AI/BI Dashboard sample page."""
    return rx.fragment(
        main_layout(
            tabbed_page_template(
                page_title="AI/BI Dashboard",
                page_description="Embed an interactive AI/BI Dashboard directly into your Reflex application.",
                try_it_content=ai_bi_dashboard_content,
                code_snippet_content=CODE_SNIPPET,
                requirements_content=ai_bi_dashboard_requirements,
            )
        ),
        on_mount=AiBiDashboardState.on_load,
    )