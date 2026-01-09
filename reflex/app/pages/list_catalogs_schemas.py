import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.list_catalogs_schemas_state import ListCatalogsSchemasState
from app import theme


def _pattern_accordion(title: str, description: str, code: str) -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            rx.accordion.header(
                rx.accordion.trigger(
                    rx.hstack(
                        rx.text(title, class_name="font-medium"),
                        rx.icon("chevron-down", class_name="h-4 w-4"),
                        justify="between",
                        width="100%",
                        align="center",
                    ),
                    class_name="flex items-center w-full px-4 py-2 text-sm font-semibold rounded-lg transition-colors",
                    color="white",
                    background_color="#3B82F6",
                    _hover={
                        "background_color": theme.ACTIVE_ITEM_BG,
                        "color": theme.ACTIVE_ITEM_TEXT,
                    },
                )
            ),
            rx.accordion.content(
                rx.vstack(
                    rx.text(description, class_name="font-semibold text-gray-700 mb-2"),
                    rx.code_block(code, language="python", width="100%"),
                    spacing="2",
                    width="100%",
                    padding="4",
                )
            ),
            value="item-1",
            style={
                "background_color": "white",
                "border": "1px solid #E5E7EB",
                "border_radius": "0.5rem",
            },
        ),
        type="single",
        collapsible=True,
        width="100%",
        class_name="mb-2",
    )


def list_catalogs_code_display() -> rx.Component:
    return rx.vstack(
        _pattern_accordion(
            "Get Catalog (get_catalog)",
            "Fetch and format catalog metadata for display in a data editor.",
            """
import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class CatalogState(rx.State):
    catalog_data: list[list[str]] = []

    @rx.event
    def load_catalogs(self):
        # List catalogs
        catalogs = w.catalogs.list()

        # Prepare data for rx.data_editor (list of lists)
        # Columns: Name, Owner, Comment, Created At
        data = []
        for c in catalogs:
            data.append([
                c.name,
                c.owner,
                c.comment or "",
                str(c.created_at) if c.created_at else ""
            ])
        self.catalog_data = data
""",
        ),
        _pattern_accordion(
            "Get Schemas for Selected Catalog (get_schemas_for_catalog)",
            "Fetch schemas for a specific catalog and format for display.",
            """
import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class SchemaState(rx.State):
    schema_data: list[list[str]] = []

    @rx.event
    def load_schemas(self, catalog_name: str):
        # List schemas for a specific catalog
        schemas = w.schemas.list(catalog_name=catalog_name)

        # Prepare data for rx.data_editor
        # Columns: Name, Owner, Comment
        data = []
        for s in schemas:
            data.append([
                s.name,
                s.owner,
                s.comment or ""
            ])
        self.schema_data = data
""",
        ),
        width="100%",
        spacing="4",
    )


def list_catalogs_schemas_requirements() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.icon("info", class_name="h-5 w-5 text-blue-600"),
                rx.text(
                    "Note: Listing catalogs requires metastore admin privileges. If you are not a metastore admin, you will only see catalogs you have privileges on.",
                    class_name="text-sm text-blue-800",
                ),
                align="center",
                spacing="2",
            ),
            class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg w-full mb-4",
        ),
        rx.grid(
            rx.vstack(
                rx.heading(
                    "Permissions (app service principal)",
                    size="4",
                    class_name="font-semibold text-gray-800",
                ),
                rx.markdown(
                    """
* `USE CATALOG`
* `USE SCHEMA`
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
                rx.markdown(
                    """
* Unity Catalog enabled workspace
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
        ),
        width="100%",
    )


def list_catalogs_schemas_content() -> rx.Component:
    """Content for the 'Try It' tab."""
    return rx.vstack(
        rx.button(
            "Get catalogs",
            on_click=ListCatalogsSchemasState.get_catalogs,
            is_loading=ListCatalogsSchemasState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
        ),
        rx.cond(
            ListCatalogsSchemasState.catalogs_data,
            rx.data_editor(
                columns=ListCatalogsSchemasState.catalog_columns,
                data=ListCatalogsSchemasState.catalogs_data,
                is_readonly=True,
                class_name="h-64 w-full mb-4",
            ),
        ),
        rx.el.hr(class_name="w-full my-4"),
        rx.vstack(
            rx.text(
                "Select a Catalog to View its Schemas",
                class_name="font-semibold text-lg",
            ),
            rx.select(
                ListCatalogsSchemasState.catalog_names,
                value=ListCatalogsSchemasState.selected_catalog,
                on_change=ListCatalogsSchemasState.set_selected_catalog,
                placeholder="Select a catalog...",
                class_name="w-full",
            ),
            rx.button(
                "Get schemas for selected catalog",
                on_click=ListCatalogsSchemasState.get_schemas_for_catalog,
                is_loading=ListCatalogsSchemasState.is_loading,
                bg=theme.PRIMARY_COLOR,
                class_name="text-white",
                disabled=~ListCatalogsSchemasState.selected_catalog,
            ),
            width="100%",
            spacing="4",
        ),
        rx.cond(
            ListCatalogsSchemasState.schemas_data,
            rx.data_editor(
                columns=ListCatalogsSchemasState.schema_columns,
                data=ListCatalogsSchemasState.schemas_data,
                is_readonly=True,
                class_name="h-64 w-full",
            ),
            rx.cond(
                ListCatalogsSchemasState.selected_catalog
                & ~ListCatalogsSchemasState.is_loading,
                rx.text("No schemas loaded.", class_name="text-gray-500 italic"),
            ),
        ),
        rx.cond(
            ListCatalogsSchemasState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(ListCatalogsSchemasState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full mt-4",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def list_catalogs_schemas_page() -> rx.Component:
    """The List Catalogs and Schemas sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="List Unity Catalog Objects",
            page_description="Browse the object hierarchy within Unity Catalog by listing all available catalogs and their corresponding schemas.",
            try_it_content=list_catalogs_schemas_content,
            code_snippet_content=list_catalogs_code_display,
            requirements_content=list_catalogs_schemas_requirements,
        )
    )