import reflex as rx
import os
import logging
from databricks.sdk import WorkspaceClient


class DownloadFileState(rx.State):
    """State for the Download File page."""

    download_file_path: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def handle_download(self):
        if not self.download_file_path:
            yield rx.toast("Please enter a file path.", level="error")
            return
        async with self:
            self.is_loading = True
        yield
        try:
            w = WorkspaceClient()
            response = w.files.download(self.download_file_path)
            file_data = response.contents.read()
            file_name = os.path.basename(self.download_file_path)
            yield rx.download(data=file_data, filename=file_name)
            yield rx.toast(f"Downloaded {file_name}", level="success")
        except Exception as e:
            logging.exception(f"Download failed: {e}")
            yield rx.toast(f"Download failed: {e}", level="error")
        finally:
            async with self:
                self.is_loading = False