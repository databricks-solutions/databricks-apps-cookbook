import reflex as rx
from app.components.page_layout import main_layout
from app import theme


def recipe_category(title: str, recipes: list[dict]) -> rx.Component:
    """A component for a category of recipes."""
    return rx.vstack(
        rx.heading(title, size="5", class_name="font-bold text-gray-800 mb-4"),
        rx.vstack(
            rx.foreach(
                recipes,
                lambda recipe: rx.link(
                    recipe["name"],
                    href=recipe["path"],
                    class_name="text-base text-gray-800 hover:text-blue-600 transition-colors",
                ),
            ),
            align="start",
            spacing="2",
        ),
        align="start",
        class_name="p-6 bg-white border border-gray-200 rounded-lg shadow-sm h-full",
    )


def link_category(title: str, links: list[dict]) -> rx.Component:
    """A component for a category of external links."""
    return rx.vstack(
        rx.heading(title, size="4", class_name="font-semibold text-gray-700 mb-3"),
        rx.vstack(
            rx.foreach(
                links,
                lambda link: rx.link(
                    link["name"],
                    href=link["href"],
                    is_external=True,
                    class_name="text-base text-blue-600 hover:underline",
                ),
            ),
            align="start",
            spacing="2",
        ),
        align="start",
    )


def introduction_content() -> rx.Component:
    """The main content for the introduction page."""
    recipe_data = {
        "Tables": [
            {"name": "Connect an OLTP database", "path": "/oltp-database"},
            {"name": "Read a Delta table", "path": "/read-delta-table"},
            {"name": "Edit a Delta table", "path": "/edit-delta-table"},
        ],
        "Volumes": [
            {"name": "Upload a file", "path": "/upload-file"},
            {"name": "Download a file", "path": "/download-file"},
        ],
        "AI / ML": [
            {"name": "Invoke a model", "path": "/invoke-model"},
            {"name": "Run vector search", "path": "/run-vector-search"},
            {"name": "Connect an MCP server", "path": "/connect-mcp-server"},
            {"name": "Invoke multi-modal LLM", "path": "/invoke-multimodal-llm"},
        ],
        "Business Intelligence": [
            {"name": "AI/BI Dashboard", "path": "/ai-bi-dashboard"},
            {"name": "Genie", "path": "/genie"},
        ],
        "Workflows": [
            {"name": "Trigger a job", "path": "/trigger-job"},
            {"name": "Retrieve job results", "path": "/retrieve-job-results"},
        ],
        "Compute": [{"name": "Connect", "path": "/connect-cluster"}],
        "Unity Catalog": [
            {"name": "List catalogs and schemas", "path": "/list-catalogs-schemas"}
        ],
        "Authentication": [
            {"name": "Get current user", "path": "/get-current-user"},
            {"name": "On-behalf-of user", "path": "/on-behalf-of-user"},
        ],
        "External services": [
            {"name": "External connections", "path": "/external-connections"},
            {"name": "Retrieve a secret", "path": "/retrieve-a-secret"},
        ],
    }
    link_data = {
        "Official documentation": [
            {
                "name": "Apps",
                "href": "https://docs.databricks.com/en/applications/index.html",
            },
            {
                "name": "Azure",
                "href": "https://learn.microsoft.com/en-us/azure/databricks/",
            },
            {
                "name": "Python SDK",
                "href": "https://databricks-sdk-py.readthedocs.io/en/latest/",
            },
        ],
        "Code samples": [
            {
                "name": "Databricks Apps Templates",
                "href": "https://github.com/databricks/databricks-app-templates",
            }
        ],
        "Blog posts": [
            {
                "name": "End-to-end RAG application",
                "href": "https://www.databricks.com/blog/end-end-rag-application-source-retrieval-databricks-platform",
            },
            {
                "name": "Building data applications",
                "href": "https://www.databricks.com/blog/building-data-applications-databricks-apps",
            },
        ],
    }
    return rx.vstack(
        rx.vstack(
            rx.heading(
                "Welcome to the Databricks Apps Cookbook!",
                size="8",
                class_name="font-extrabold text-gray-900",
            ),
            rx.text(
                "Are you ready to serve some tasty apps to your users? You're in the right place!",
                class_name="text-xl text-gray-600",
            ),
            rx.text(
                "Explore the recipes via the sidebar to quickly build flexible and engaging data apps directly on Databricks.",
                class_name="text-xl text-gray-600",
            ),
            rx.markdown(
                "Have a great recipe to share? Raise a pull request on the [GitHub repository](https://github.com/pbv0/databricks-apps-cookbook)!",
                class_name="text-xl text-gray-600",
            ),
            align="start",
            spacing="4",
            class_name="py-16",
        ),
        rx.vstack(
            rx.heading("Recipes", size="6", class_name="font-bold text-gray-800"),
            rx.el.hr(class_name="w-full my-6"),
            rx.grid(
                rx.foreach(
                    list(recipe_data.items()),
                    lambda item: recipe_category(item[0], item[1]),
                ),
                columns="1fr 1fr 1fr 1fr",
                spacing="8",
                width="100%",
            ),
            align="start",
            width="100%",
        ),
        rx.vstack(
            rx.heading("Links", size="6", class_name="font-bold text-gray-800 mt-12"),
            rx.el.hr(class_name="w-full my-6"),
            rx.grid(
                rx.foreach(
                    list(link_data.items()),
                    lambda item: link_category(item[0], item[1]),
                ),
                columns="1fr 1fr 1fr",
                spacing="8",
                width="100%",
            ),
            align="start",
            width="100%",
        ),
        align="start",
        spacing="8",
        width="100%",
    )


def introduction_page() -> rx.Component:
    return main_layout(introduction_content())