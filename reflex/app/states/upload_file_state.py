import reflex as rx
import io
import logging
from databricks.sdk import WorkspaceClient


def check_upload_permissions(volume_name: str):
    try:
        w = WorkspaceClient()
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
        logging.exception(f"Error: {e}")
        return f"Error: {e}"


class UploadFileState(rx.State):
    """State for the Upload File page."""

    upload_volume_path: str = ""
    volume_check_success: bool = False
    permission_result: str = ""
    is_checking: bool = False
    is_loading: bool = False
    is_uploading: bool = False
    error_message: str = ""
    uploaded_files: list[str] = []

    @rx.event
    def set_upload_volume_path(self, value: str):
        self.upload_volume_path = value

    @rx.event(background=True)
    async def check_volume_permissions(self):
        async with self:
            self.is_checking = True
            self.permission_result = ""
            self.volume_check_success = False
        result = check_upload_permissions(self.upload_volume_path)
        async with self:
            self.permission_result = result
            if "validated" in result:
                self.volume_check_success = True
            self.is_checking = False

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        self.is_uploading = True
        yield
        try:
            w = WorkspaceClient()
            parts = self.upload_volume_path.strip().split(".")
            if len(parts) != 3:
                yield rx.toast(
                    "Invalid volume path format. Use catalog.schema.volume",
                    level="error",
                )
                self.is_uploading = False
                return
            catalog = parts[0]
            schema = parts[1]
            volume_name = parts[2]
            for file in files:
                file_bytes = await file.read()
                binary_data = io.BytesIO(file_bytes)
                file_name = file.filename
                volume_file_path = (
                    f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
                )
                w.files.upload(volume_file_path, binary_data, overwrite=True)
                self.uploaded_files.append(file_name)
                yield rx.toast(
                    f"Uploaded {file_name} to {volume_file_path}", level="success"
                )
        except Exception as e:
            logging.exception(f"Upload failed: {e}")
            yield rx.toast(f"Upload failed: {e}", level="error")
        finally:
            self.is_uploading = False