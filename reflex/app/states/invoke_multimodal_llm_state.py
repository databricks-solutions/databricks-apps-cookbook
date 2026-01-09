import reflex as rx
import io
import base64
import logging
import asyncio
from databricks.sdk import WorkspaceClient


def pillow_image_to_base64_string(img) -> str:
    """Encodes PIL Image into a base64 string."""
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def chat_with_mllm(
    model_name: str,
    prompt: str,
    base64_image: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 512,
):
    """
    Calls the Databricks Model Serving endpoint using the OpenAI SDK format.
    Constructs the message payload depending on whether an image is provided.
    """
    w = WorkspaceClient()
    model_client = w.serving_endpoints.get_open_ai_client()
    messages = []
    if base64_image:
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        )
    else:
        messages.append({"role": "user", "content": prompt})
    return model_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )


class InvokeMultimodalLlmState(rx.State):
    """State for Invoke Multimodal LLM page."""

    endpoint_names: list[str] = []
    selected_model: str = ""
    prompt: str = "Describe the image(s) as an alternative text"
    uploaded_image: str = ""
    result: str = ""
    is_loading: bool = False
    error_message: str = ""

    @rx.event
    def set_selected_model(self, value: str):
        self.selected_model = value

    @rx.event
    def set_prompt(self, value: str):
        self.prompt = value

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
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Process the uploaded image."""
        if not files:
            return
        file = files[0]
        upload_data = await file.read()
        try:
            from PIL import Image

            image = Image.open(io.BytesIO(upload_data))
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            base64_str = pillow_image_to_base64_string(image)
            self.uploaded_image = base64_str
        except Exception as e:
            logging.exception(f"Error processing image: {e}")
            self.error_message = f"Error processing image: {e}"

    @rx.event(background=True)
    async def invoke_llm(self):
        async with self:
            if not self.selected_model:
                self.error_message = "Please select a model."
                return
            if not self.uploaded_image:
                self.error_message = "Please upload an image to proceed."
                return
            self.is_loading = True
            self.error_message = ""
            self.result = ""
            current_model = self.selected_model
            current_prompt = self.prompt
            current_image = self.uploaded_image
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, chat_with_mllm, current_model, current_prompt, current_image
            )
            content = response.choices[0].message.content
            async with self:
                self.result = content
        except Exception as e:
            logging.exception(f"Error invoking MLLM: {e}")
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False