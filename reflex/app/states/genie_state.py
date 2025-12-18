import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from typing import Any
import logging
import asyncio


class GenieState(rx.State):
    """State for Genie page."""

    genie_space_id: str = ""
    conversation_id: str = ""
    input_text: str = ""
    messages: list[dict] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.var
    def open_genie_url(self) -> str:
        """Constructs the URL to open the conversation in the Genie UI."""
        if not self.genie_space_id or not self.conversation_id:
            return ""
        cfg = Config()
        host = cfg.host.rstrip("/")
        return f"{host}/genie/spaces/{self.genie_space_id}/conversations/{self.conversation_id}"

    @rx.event
    def reset_conversation(self):
        """Resets the current conversation."""
        self.conversation_id = ""
        self.messages = []
        self.input_text = ""
        self.error_message = ""

    @rx.event
    def set_genie_space_id(self, value: str):
        self.genie_space_id = value
        self.reset_conversation()

    @rx.event
    def set_input_text(self, value: str):
        self.input_text = value

    @rx.event
    def add_message(self, role: str, type_: str, content: any):
        self.messages.append({"role": role, "type": type_, "content": content})

    @rx.event
    async def get_query_result(self, statement_id: str) -> list[dict]:
        """Fetches the result of a Genie-executed statement, handling chunking."""
        w = WorkspaceClient()
        try:
            result = w.statement_execution.get_statement(statement_id)
            if not result.result:
                return []
            data_array = result.result.data_array or []
            next_chunk = result.result.next_chunk_index
            while next_chunk:
                chunk = w.statement_execution.get_statement_result_chunk_n(
                    statement_id, next_chunk
                )
                if chunk.data_array:
                    data_array.extend(chunk.data_array)
                next_chunk = chunk.next_chunk_index
            cols = [c.name for c in result.manifest.schema.columns]
            return [dict(zip(cols, row)) for row in data_array]
        except Exception as e:
            logging.exception(f"Error fetching query result: {e}")
            return []

    @rx.event
    def handle_key_down(self, key: str):
        if key == "Enter":
            return GenieState.send_message

    @rx.event
    async def process_genie_response(self, response: Any):
        """Parses the Genie response and updates the chat history."""
        if hasattr(response, "conversation_id") and response.conversation_id:
            self.conversation_id = response.conversation_id
        if not response.attachments:
            return
        for attachment in response.attachments:
            if attachment.text:
                self.add_message("genie", "text", attachment.text.content)
            elif attachment.query:
                description = getattr(attachment.query, "description", None)
                if description:
                    self.add_message("genie", "text", description)
                query_code = getattr(attachment.query, "query", None) or getattr(
                    attachment.query, "query_string", None
                )
                if query_code:
                    self.add_message("genie", "code", query_code)
                stmt_id = getattr(attachment.query, "statement_id", None)
                if stmt_id:
                    data = await self.get_query_result(stmt_id)
                    if data:
                        self.add_message("genie", "data", data)

    @rx.event(background=True)
    async def send_message(self):
        """Sends a message to Genie and processes the response."""
        async with self:
            if not self.genie_space_id:
                self.error_message = "Please enter a Genie Space ID."
                return
            if not self.input_text:
                return
            user_input = self.input_text
            self.input_text = ""
            self.add_message("user", "text", user_input)
            self.is_loading = True
            self.error_message = ""
            space_id = self.genie_space_id
            conversation_id = self.conversation_id
        yield
        try:
            w = WorkspaceClient()
            loop = asyncio.get_running_loop()

            def _call_genie(sid, cid, content):
                if not cid:
                    return w.genie.start_conversation_and_wait(
                        space_id=sid, content=content
                    )
                else:
                    return w.genie.create_message_and_wait(
                        space_id=sid, conversation_id=cid, content=content
                    )

            response = await loop.run_in_executor(
                None, _call_genie, space_id, conversation_id, user_input
            )
            async with self:
                await self.process_genie_response(response)
        except Exception as e:
            logging.exception(f"Genie error: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False