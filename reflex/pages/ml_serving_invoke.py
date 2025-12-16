import reflex_enterprise as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
import json

class State(rx.State):
    response: str = ""
    model_name: str = "llm-text-completions-model"

    def _set_response(self, resp):
        try:
            self.response = json.dumps(resp.as_dict(), indent=2)
        except Exception:
            try:
                self.response = json.dumps(resp.json(), indent=2)
            except Exception:
                self.response = getattr(resp, "text", str(resp))

    def query_dataframe_split(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="custom-regression-model",
            dataframe_split={
                "columns": ["feature1", "feature2"],
                "data": [[1.5, 2.5]]
            }
        )
        self._set_response(resp)

    def query_dataframe_records(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="custom-regression-model",
            dataframe_records={
                "feature1": [1.5],
                "feature2": [2.5]
            }
        )
        self._set_response(resp)

    def query_instances(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="tensor-processing-model",
            instances=[[1.0, 2.0, 3.0]],
        )
        self._set_response(resp)

    def query_inputs(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="tensor-processing-model",
            inputs={"input1": [1.0, 2.0, 3.0], "input2": [4.0, 5.0, 6.0]},
        )
        self._set_response(resp)

    def query_prompt(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="llm-text-completions-model",
            prompt="Generate a short checklist for deploying Databricks Apps.",
            temperature=0.5,
        )
        self._set_response(resp)

    def query_messages(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="chat-assistant-model",
            messages=[
                ChatMessage(role=ChatMessageRole.SYSTEM, content="You are a helpful assistant."),
                ChatMessage(role=ChatMessageRole.USER, content="Provide tips for deploying Databricks Apps."),
            ],
        )
        self._set_response(resp)

    def query_input_embedding(self):
        w = WorkspaceClient()
        resp = w.serving_endpoints.query(
            name="embedding-model",
            input="Databricks provides a unified analytics platform.",
        )
        self._set_response(resp)

def index() -> rx.Component:
    return rx.vstack(
        rx.heading("Model Serving Invoke — Reflex"),
        rx.hstack(
            rx.vstack(
                rx.button("dataframe_split", on_click=State.query_dataframe_split),
                rx.button("dataframe_records", on_click=State.query_dataframe_records),
                rx.button("instances", on_click=State.query_instances),
                rx.button("inputs", on_click=State.query_inputs),
                spacing="3"
            ),
            rx.vstack(
                rx.button("prompt (LLM)", on_click=State.query_prompt),
                rx.button("messages (chat)", on_click=State.query_messages),
                rx.button("input (embedding)", on_click=State.query_input_embedding),
                spacing="3"
            ),
            spacing="6"
        ),
        rx.box(rx.text(State.response), padding="4", width="100%", white_space="pre"),
        spacing="4",
        padding="4"
    )
