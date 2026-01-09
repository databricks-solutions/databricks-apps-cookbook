import reflex as rx
from databricks.sdk import WorkspaceClient
import json
import asyncio
import logging


class GetCurrentUserState(rx.State):
    """State for Get Current User page."""

    header_email: str = ""
    header_username: str = ""
    header_user: str = ""
    header_ip: str = ""
    header_token: str = ""
    all_headers_json: str = ""
    user_id: str = ""
    user_name: str = ""
    user_display_name: str = ""
    user_active: bool = False
    user_external_id: str = ""
    groups_count: int = 0
    entitlements_count: int = 0
    user_json: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def get_user_headers(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            headers = self.router.headers
            try:

                @rx.event
                def to_serializable(obj):
                    if isinstance(obj, (str, int, float, bool, type(None))):
                        return obj
                    if hasattr(obj, "items"):
                        return {str(k): to_serializable(v) for k, v in obj.items()}
                    if isinstance(obj, (list, tuple)):
                        return [to_serializable(i) for i in obj]
                    return str(obj)

                headers_dict = {}
                for k, v in vars(headers).items():
                    if not k.startswith("_"):
                        headers_dict[k] = to_serializable(v)
            except Exception as e:
                logging.exception(f"Error serializing headers: {e}")
                headers_dict = {"error": f"Could not serialize headers: {e}"}
            self.all_headers_json = json.dumps(headers_dict, indent=2)
            self.header_email = getattr(headers, "x_forwarded_email", "")
            self.header_username = getattr(
                headers, "x_forwarded_preferred_username", ""
            )
            self.header_user = getattr(headers, "x_forwarded_user", "")
            self.header_ip = getattr(headers, "x_real_ip", "")
            self.header_token = getattr(headers, "x_forwarded_access_token", "")
        try:
            if self.header_token:
                loop = asyncio.get_running_loop()

                @rx.event
                def fetch_user_info(token):
                    w = WorkspaceClient(token=token, auth_type="pat")
                    return w.current_user.me()

                me = await loop.run_in_executor(
                    None, fetch_user_info, self.header_token
                )
                async with self:
                    self.user_id = me.id
                    self.user_name = me.user_name or ""
                    self.user_display_name = me.display_name or ""
                    self.user_active = me.active
                    self.user_external_id = me.external_id or ""
                    self.groups_count = len(me.groups) if me.groups else 0
                    self.entitlements_count = (
                        len(me.entitlements) if me.entitlements else 0
                    )
                    self.user_json = json.dumps(me.as_dict(), indent=2)
            else:
                async with self:
                    pass
        except Exception as e:
            logging.exception(f"Error fetching current user: {e}")
            async with self:
                self.error_message = f"Error fetching user info: {e}"
        finally:
            async with self:
                self.is_loading = False