import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.states.download_file_state import DownloadFileState
from app import theme

CODE_SNIPPET = """
import reflex as rx
import os
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class DownloadFileState(rx.State):
    download_file_path: str = ""

    async def handle_download(self):
        response = w.files.download(self.download_file_path)
        file_data = response.contents.read()
        file_name = os.path.basename(self.download_file_path)

        return rx.download(data=file_data, filename=file_name)
"""


def download_file_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
* `USE CATALOG` on the catalog of the volume
* `USE SCHEMA` on the schema of the volume
* `READ VOLUME` on the volume

See [Privileges required for volume operations](https://docs.databricks.com/en/volumes/privileges.html#privileges-required-for-volume-operations) for more information.
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
            rx.markdown("* Unity Catalog volume", class_name="text-sm text-gray-600"),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.markdown(
                """
* [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
* [Reflex](https://pypi.org/project/reflex/) - `reflex`
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


def download_file_content() -> rx.Component:
    """Content for the 'Try It' tab of the Download File page."""
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Specify a path to a file in a Unity Catalog volume:",
                class_name="font-semibold text-sm",
            ),
            rx.input(
                placeholder="/Volumes/catalog/schema/volume_name/file.csv",
                on_change=DownloadFileState.set_download_file_path,
                class_name="w-full",
                default_value=DownloadFileState.download_file_path,
            ),
            width="100%",
        ),
        rx.button(
            "Download",
            on_click=DownloadFileState.handle_download,
            is_loading=DownloadFileState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            DownloadFileState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(DownloadFileState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def download_file_page() -> rx.Component:
    """The Download a File from Volume sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Download a File from a Volume",
            page_description="Download files from a Databricks Volume directly to the user's browser.",
            try_it_content=download_file_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=download_file_requirements,
        )
    )