import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)

CODE_SNIPPET = """
import reflex as rx
import io
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def check_upload_permissions(volume_name: str):
    try:
        volume = w.volumes.read(name=volume_name)
        current_user = w.current_user.me()
        grants = w.grants.get_effective(
            securable_type="volume",
            full_name=volume.full_name,
            principal=current_user.user_name,
        )

        if not grants or not grants.privilege_assignments:
            return "Insufficient permissions: No grants found."

        for assignment in grants.privilege_assignments:
            for privilege in assignment.privileges:
                if privilege.privilege.value in ["ALL_PRIVILEGES", "WRITE_VOLUME"]:
                    return "Volume and permissions validated"

        return "Insufficient permissions: Required privileges not found."
    except Exception as e:
        return f"Error: {e}"

class UploadFileState(rx.State):
    upload_volume_path: str = ""
    volume_check_success: bool = False
    permission_result: str = ""
    is_checking: bool = False
    is_uploading: bool = False
    uploaded_files: list[str] = []

    @rx.event
    async def check_volume_permissions(self):
        self.is_checking = True
        self.permission_result = ""
        self.volume_check_success = False
        yield

        result = check_upload_permissions(self.upload_volume_path)

        self.permission_result = result
        if "validated" in result:
            self.volume_check_success = True
        self.is_checking = False

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files: return
        self.is_uploading = True
        yield
        try:
            parts = self.upload_volume_path.strip().split(".")
            catalog, schema, volume_name = parts[0], parts[1], parts[2]
            for file in files:
                file_bytes = await file.read()
                binary_data = io.BytesIO(file_bytes)
                path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file.filename}"
                w.files.upload(path, binary_data, overwrite=True)
                self.uploaded_files.append(file.filename)
                yield rx.toast(f"Uploaded {file.filename} to {path}", level="success")
        except Exception as e:
            yield rx.toast(f"Upload failed: {e}", level="error")
        finally:
            self.is_uploading = False
"""
from app.states.upload_file_state import UploadFileState
from app import theme


def upload_file_requirements() -> rx.Component:
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
* `READ VOLUME` and `WRITE VOLUME` on the volume

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


def upload_file_content() -> rx.Component:
    """Content for the 'Try It' tab of the Upload File page."""
    return rx.vstack(
        rx.text(
            "Volume Path (catalog.schema.volume)", class_name="font-semibold text-sm"
        ),
        rx.input(
            placeholder="main.marketing.raw_files",
            on_change=UploadFileState.set_upload_volume_path,
            class_name="w-full",
            default_value=UploadFileState.upload_volume_path,
        ),
        rx.button(
            "Check Volume and permissions",
            on_click=UploadFileState.check_volume_permissions,
            is_loading=UploadFileState.is_checking,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white",
        ),
        rx.cond(
            UploadFileState.permission_result != "",
            rx.box(
                rx.text(UploadFileState.permission_result),
                class_name=rx.cond(
                    UploadFileState.volume_check_success,
                    "p-4 bg-green-100 text-green-800 rounded-lg w-full",
                    "p-4 bg-red-100 text-red-800 rounded-lg w-full",
                ),
            ),
        ),
        rx.cond(
            UploadFileState.volume_check_success,
            rx.vstack(
                rx.upload.root(
                    rx.vstack(
                        rx.button(
                            "Select File",
                            color=theme.PRIMARY_COLOR,
                            bg="white",
                            border=f"1px solid {theme.PRIMARY_COLOR}",
                        ),
                        rx.text("Drag and drop files here or click to select files"),
                        align="center",
                        spacing="2",
                    ),
                    id="upload1",
                    border="1px dotted rgb(107, 114, 128)",
                    padding="2em",
                    class_name="w-full rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors",
                ),
                rx.vstack(
                    rx.foreach(
                        rx.selected_files("upload1"),
                        lambda file: rx.text(file, class_name="text-sm text-gray-600"),
                    ),
                    align="start",
                    class_name="w-full",
                ),
                rx.cond(
                    rx.selected_files("upload1").length() > 0,
                    rx.button(
                        "Upload",
                        on_click=UploadFileState.handle_upload(
                            rx.upload_files(upload_id="upload1")
                        ),
                        is_loading=UploadFileState.is_uploading,
                        bg=theme.PRIMARY_COLOR,
                        class_name="text-white",
                    ),
                ),
                width="100%",
                spacing="4",
            ),
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def upload_file_page() -> rx.Component:
    """The Upload a File to Volume sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Upload a File to a Volume",
            page_description="Upload files from your local system directly into a Databricks Volume for use in your workspaces.",
            try_it_content=upload_file_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=upload_file_requirements,
        )
    )