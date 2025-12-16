import reflex as rx
from typing import TypedDict


class NavItem(TypedDict):
    name: str
    path: str


class NavSection(TypedDict):
    section_name: str
    icon: str
    items: list[NavItem]


class CookbookState(rx.State):
    """The state for the cookbook application."""

    navigation_items: list[NavSection] = [
        {
            "section_name": "Tables",
            "icon": "table-2",
            "items": [
                {"name": "OLTP Database", "path": "/oltp-database"},
                {"name": "Read a Delta table", "path": "/read-delta-table"},
                {"name": "Edit a Delta table", "path": "/edit-delta-table"},
            ],
        },
        {
            "section_name": "Volumes",
            "icon": "folder-open",
            "items": [
                {"name": "Upload a file", "path": "/upload-file"},
                {"name": "Download a file", "path": "/download-file"},
            ],
        },
        {
            "section_name": "AI / ML",
            "icon": "brain-circuit",
            "items": [
                {"name": "Invoke a model", "path": "/invoke-model"},
                {"name": "Run vector search", "path": "/run-vector-search"},
                {"name": "Connect an MCP server", "path": "/connect-mcp-server"},
                {"name": "Invoke multi-modal LLM", "path": "/invoke-multimodal-llm"},
            ],
        },
        {
            "section_name": "Business Intelligence",
            "icon": "bar-chart-big",
            "items": [
                {"name": "AI/BI Dashboard", "path": "/ai-bi-dashboard"},
                {"name": "Genie", "path": "/genie"},
            ],
        },
        {
            "section_name": "Workflows",
            "icon": "recycle",
            "items": [
                {"name": "Trigger a job", "path": "/trigger-job"},
                {"name": "Retrieve job results", "path": "/retrieve-job-results"},
            ],
        },
        {
            "section_name": "Compute",
            "icon": "server",
            "items": [{"name": "Connect", "path": "/connect-cluster"}],
        },
        {
            "section_name": "Unity Catalog",
            "icon": "database",
            "items": [
                {"name": "List catalogs and schemas", "path": "/list-catalogs-schemas"}
            ],
        },
        {
            "section_name": "Authentication",
            "icon": "key-round",
            "items": [
                {"name": "Get current user", "path": "/get-current-user"},
                {"name": "On-behalf-of-user", "path": "/on-behalf-of-user"},
            ],
        },
        {
            "section_name": "External services",
            "icon": "plug-zap",
            "items": [
                {"name": "External connections", "path": "/external-connections"},
                {"name": "Retrieve a secret", "path": "/retrieve-a-secret"},
            ],
        },
    ]
    collapsed_sections: dict[str, bool] = {
        "Tables": False,
        "Volumes": False,
        "AI / ML": False,
        "Business Intelligence": False,
        "Workflows": False,
        "Compute": False,
        "Unity Catalog": False,
        "Authentication": False,
        "External services": False,
    }

    @rx.var
    def current_page_path(self) -> str:
        return self.router.page.path or ""

    @rx.event
    def toggle_section(self, section_name: str):
        self.collapsed_sections[section_name] = not self.collapsed_sections[
            section_name
        ]