import reflex as rx
import requests
import logging
import time
from databricks.sdk.core import Config


def get_published_dashboards() -> dict[str, str]:
    """
    Fetches the list of published AI/BI dashboards using the Databricks API.
    Returns a dictionary mapping dashboard display names to their IDs.
    """
    cfg = Config()
    token = list(cfg.authenticate().values())[0].split(" ")[1]
    headers = {"Authorization": f"Bearer {token}"}
    host = cfg.host.rstrip("/")
    url = f"{host}/api/2.0/lakeview/dashboards"

    def fetch_with_retry(target_url):
        retries = 3
        delay = 1
        for attempt in range(retries + 1):
            response = requests.get(target_url, headers=headers)
            if response.status_code == 429:
                if attempt < retries:
                    logging.warning(
                        f"Rate limit hit (429) when fetching dashboards. Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue
            return response
        return None

    response = fetch_with_retry(url)
    if not response:
        return {}
    response.raise_for_status()
    data = response.json()
    published_dashboards = {}
    for dashboard in data.get("dashboards", []):
        dashboard_id = dashboard.get("dashboard_id")
        display_name = dashboard.get("display_name", "Untitled")
        if not dashboard_id:
            continue
        pub_url = f"{host}/api/2.0/lakeview/dashboards/{dashboard_id}/published"
        pub_response = fetch_with_retry(pub_url)
        if pub_response and pub_response.status_code == 200:
            published_dashboards[display_name] = dashboard_id
    return published_dashboards


class AiBiDashboardState(rx.State):
    """State for the AI/BI Dashboard page."""

    dashboard_options: dict[str, str] = {}
    selected_dashboard: str = ""
    iframe_source: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def dashboard_names(self) -> list[str]:
        return list(self.dashboard_options.keys())

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            dashboards = get_published_dashboards()
            async with self:
                self.dashboard_options = dashboards
                if self.dashboard_names:
                    self.selected_dashboard = self.dashboard_names[0]
                    self.update_iframe_source()
        except Exception as e:
            logging.exception(f"Error loading dashboards: {e}")
            async with self:
                self.error_message = f"Error loading dashboards: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def update_iframe_source(self):
        """Updates the iframe URL based on the selected dashboard."""
        if not self.selected_dashboard:
            self.iframe_source = ""
            return
        dashboard_id = self.dashboard_options.get(self.selected_dashboard)
        if dashboard_id:
            cfg = Config()
            host = cfg.host.rstrip("/")
            self.iframe_source = f"{host}/embed/dashboardsv3/{dashboard_id}"

    @rx.event
    def set_selected_dashboard(self, value: str):
        self.selected_dashboard = value
        self.update_iframe_source()