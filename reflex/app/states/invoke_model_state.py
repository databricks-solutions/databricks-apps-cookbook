import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
import json
import logging


class InvokeModelState(rx.State):
    """State for the Invoke Model page."""

    endpoint_names: list[str] = []
    selected_model: str = ""
    model_type: str = "LLM"
    temperature: float = 1.0
    prompt: str = ""
    input_value: str = ""
    response_data: dict = {}
    is_loading: bool = False
    is_invoking: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            w = WorkspaceClient()
            endpoints = w.serving_endpoints.list()
            names = [e.name for e in endpoints]
            async with self:
                self.endpoint_names = names
                if names and (not self.selected_model):
                    self.selected_model = names[0]
        except Exception as e:
            logging.exception(f"Error fetching endpoints: {e}")
            async with self:
                self.error_message = f"Error fetching endpoints: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def set_selected_model(self, value: str):
        self.selected_model = value

    @rx.event
    def set_model_type(self, value: str):
        self.model_type = value

    @rx.event
    def set_temperature(self, value: str):
        try:
            self.temperature = float(value)
        except ValueError as e:
            logging.exception(f"Error setting temperature: {e}")

    @rx.event
    def set_prompt(self, value: str):
        self.prompt = value

    @rx.event
    def set_input_value(self, value: str):
        self.input_value = value

    @rx.event(background=True)
    async def invoke_llm(self):
        async with self:
            current_model = self.selected_model
            current_prompt = self.prompt
            current_temperature = self.temperature
            if not current_model:
                self.error_message = "Please select a model."
                return
            if not current_prompt:
                self.error_message = "Please enter a prompt."
                return
            self.is_loading = True
            self.error_message = ""
            self.response_data = {}
        yield
        try:
            w = WorkspaceClient()
            messages = [ChatMessage(role=ChatMessageRole.USER, content=current_prompt)]
            response = w.serving_endpoints.query(
                name=current_model, messages=messages, temperature=current_temperature
            )
            async with self:
                self.response_data = response.as_dict()
        except Exception as e:
            logging.exception(f"Error invoking LLM: {e}")
            async with self:
                self.error_message = f"Error invoking LLM: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def invoke_traditional_ml(self):
        async with self:
            if not self.selected_model:
                self.error_message = "Please select a model."
                return
            if not self.input_value:
                self.error_message = "Please enter input data."
                return
            self.is_loading = True
            self.error_message = ""
            self.response_data = {}
        yield
        try:
            input_json = json.loads(self.input_value)
            w = WorkspaceClient()
            response = w.serving_endpoints.query(
                name=self.selected_model, dataframe_records=input_json
            )
            async with self:
                self.response_data = response.as_dict()
        except json.JSONDecodeError:
            logging.exception("Invalid JSON input")
            async with self:
                self.error_message = "Invalid JSON input."
        except Exception as e:
            logging.exception(f"Error invoking model: {e}")
            async with self:
                self.error_message = f"Error invoking model: {e}"
        finally:
            async with self:
                self.is_loading = False