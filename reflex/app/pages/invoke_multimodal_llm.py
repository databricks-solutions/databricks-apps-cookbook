import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.states.invoke_multimodal_llm_state import InvokeMultimodalLlmState
from app import theme

CODE_SNIPPET = """
import reflex as rx
import io
import base64
from PIL import Image
from databricks.sdk import WorkspaceClient

# Initialize Databricks and OpenAI-compatible client
w = WorkspaceClient()
model_client = w.serving_endpoints.get_open_ai_client()

def pillow_image_to_base64_string(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def chat_with_mllm(model_name: str, prompt: str, base64_image: str | None = None):
    messages = []
    if base64_image:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    return model_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.1,
        max_tokens=512,
    )

class InvokeMultimodalLlmState(rx.State):
    endpoint_names: list[str] = []
    selected_model: str = ""
    prompt: str = "Describe this image"
    uploaded_image: str = ""
    result: str = ""
    is_loading: bool = False

    @rx.event
    def on_load(self):
        endpoints = w.serving_endpoints.list()
        self.endpoint_names = [e.name for e in endpoints]
        if self.endpoint_names:
            self.selected_model = self.endpoint_names[0]

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files: return
        file = files[0]
        data = await file.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        self.uploaded_image = pillow_image_to_base64_string(img)

    @rx.event
    def invoke_llm(self):
        self.is_loading = True
        yield
        try:
            response = chat_with_mllm(
                self.selected_model, self.prompt, self.uploaded_image
            )
            self.result = response.choices[0].message.content
        except Exception as e:
            self.result = f"Error: {e}"
        finally:
            self.is_loading = False
"""


def invoke_multimodal_llm_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                "* `CAN QUERY` on the model serving endpoint",
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
                "* Multi-modal Model Serving endpoint",
                class_name="text-sm text-gray-600",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        rx.vstack(
            rx.heading(
                "Dependencies", size="4", class_name="font-semibold text-gray-800"
            ),
            rx.el.ul(
                rx.el.li(
                    rx.link(
                        "databricks-sdk",
                        href="https://pypi.org/project/databricks-sdk/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                rx.el.li(
                    rx.link(
                        "reflex",
                        href="https://pypi.org/project/reflex/",
                        is_external=True,
                        class_name="text-blue-600 hover:underline",
                    )
                ),
                class_name="list-disc list-inside text-sm text-gray-600 pl-2",
            ),
            class_name="p-4 bg-gray-50 rounded-lg h-full",
            align="start",
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def invoke_multimodal_llm_content() -> rx.Component:
    """Content for the 'Try It' tab of the Invoke Multi-modal LLM page."""
    return rx.vstack(
        rx.vstack(
            rx.text(
                "Select a multi-modal Model Serving endpoint",
                class_name="font-semibold text-sm",
            ),
            rx.select(
                InvokeMultimodalLlmState.endpoint_names,
                value=InvokeMultimodalLlmState.selected_model,
                on_change=InvokeMultimodalLlmState.set_selected_model,
                placeholder="Select an endpoint...",
                class_name="w-full",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Enter your prompt:", class_name="font-semibold text-sm"),
            rx.text_area(
                on_change=InvokeMultimodalLlmState.set_prompt,
                placeholder="Describe or ask something about the image...",
                class_name="w-full h-24",
                default_value=InvokeMultimodalLlmState.prompt,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text(
                "Select an image (JPG, JPEG, or PNG)",
                class_name="font-semibold text-sm",
            ),
            rx.upload.root(
                rx.vstack(
                    rx.button(
                        "Select Image",
                        color=theme.PRIMARY_COLOR,
                        bg="white",
                        border=f"1px solid {theme.PRIMARY_COLOR}",
                    ),
                    rx.text("Drag and drop or click to select"),
                    align="center",
                    spacing="2",
                ),
                id="mllm_upload",
                accept={"image/*": [".png", ".jpg", ".jpeg"]},
                max_files=1,
                border="1px dotted rgb(107, 114, 128)",
                padding="2em",
                class_name="w-full rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors",
            ),
            rx.cond(
                rx.selected_files("mllm_upload").length() > 0,
                rx.button(
                    "Upload Selected Image",
                    on_click=InvokeMultimodalLlmState.handle_upload(
                        rx.upload_files(upload_id="mllm_upload")
                    ),
                    bg=theme.PRIMARY_COLOR,
                    class_name="text-white mt-2",
                ),
            ),
            width="100%",
        ),
        rx.cond(
            InvokeMultimodalLlmState.uploaded_image,
            rx.box(
                rx.text("Uploaded image", class_name="font-semibold text-xs mb-2"),
                rx.image(
                    src=f"data:image/jpeg;base64,{InvokeMultimodalLlmState.uploaded_image}",
                    class_name="max-h-64 object-contain rounded-lg border",
                ),
                class_name="p-4 bg-gray-50 rounded-lg w-full",
            ),
        ),
        rx.button(
            "Invoke LLM",
            on_click=InvokeMultimodalLlmState.invoke_llm,
            is_loading=InvokeMultimodalLlmState.is_loading,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white w-full",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            InvokeMultimodalLlmState.is_loading,
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Processing...", class_name="text-gray-500"),
                align="center",
                justify="center",
                class_name="w-full h-32 bg-gray-50 rounded-lg",
            ),
        ),
        rx.cond(
            InvokeMultimodalLlmState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(InvokeMultimodalLlmState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            InvokeMultimodalLlmState.result,
            rx.vstack(
                rx.text("Response", class_name="font-semibold text-sm"),
                rx.box(
                    rx.markdown(InvokeMultimodalLlmState.result),
                    class_name="p-4 bg-white border rounded-lg w-full overflow-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        spacing="4",
        width="100%",
        align="start",
    )


def invoke_multimodal_llm_page() -> rx.Component:
    """The Invoke Multi-modal LLM sample page."""
    return rx.fragment(
        main_layout(
            tabbed_page_template(
                page_title="Invoke a Multi-modal LLM",
                page_description="Send text prompts and image data to a multi-modal large language model endpoint.",
                try_it_content=invoke_multimodal_llm_content,
                code_snippet_content=CODE_SNIPPET,
                requirements_content=invoke_multimodal_llm_requirements,
            )
        ),
        on_mount=InvokeMultimodalLlmState.on_load,
    )