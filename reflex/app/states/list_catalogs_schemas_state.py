import reflex as rx
from databricks.sdk import WorkspaceClient
import logging


class ListCatalogsSchemasState(rx.State):
    """State for List Catalogs and Schemas page."""

    catalogs_data: list[list[str]] = []
    catalog_columns: list[dict[str, str]] = [
        {"title": "Name", "id": "name", "type": "str"},
        {"title": "Owner", "id": "owner", "type": "str"},
        {"title": "Comment", "id": "comment", "type": "str"},
        {"title": "Created At", "id": "created_at", "type": "str"},
    ]
    schemas_data: list[list[str]] = []
    schema_columns: list[dict[str, str]] = [
        {"title": "Name", "id": "name", "type": "str"},
        {"title": "Owner", "id": "owner", "type": "str"},
        {"title": "Comment", "id": "comment", "type": "str"},
    ]
    catalog_names: list[str] = []
    selected_catalog: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def get_catalogs(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.catalogs_data = []
            self.catalog_names = []
            self.schemas_data = []
            self.selected_catalog = ""
        try:
            w = WorkspaceClient()
            catalogs = w.catalogs.list()
            data = []
            names = []
            for c in catalogs:
                names.append(c.name)
                data.append(
                    [
                        c.name,
                        c.owner,
                        c.comment or "",
                        str(c.created_at) if c.created_at else "",
                    ]
                )
            async with self:
                self.catalogs_data = data
                self.catalog_names = names
                if names:
                    self.selected_catalog = names[0]
        except Exception as e:
            logging.exception(f"Error fetching catalogs: {e}")
            async with self:
                self.error_message = f"Error fetching catalogs: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_selected_catalog(self, value: str):
        self.selected_catalog = value
        self.schemas_data = []

    @rx.event(background=True)
    async def get_schemas_for_catalog(self):
        async with self:
            if not self.selected_catalog:
                self.error_message = "Please select a catalog first."
                return
            self.is_loading = True
            self.error_message = ""
            self.schemas_data = []
        try:
            w = WorkspaceClient()
            schemas = w.schemas.list(catalog_name=self.selected_catalog)
            data = []
            for s in schemas:
                data.append([s.name, s.owner, s.comment or ""])
            async with self:
                self.schemas_data = data
        except Exception as e:
            logging.exception(f"Error fetching schemas: {e}")
            async with self:
                self.error_message = f"Error fetching schemas: {e}"
        finally:
            async with self:
                self.is_loading = False