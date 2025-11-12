import io
import base64
import streamlit as st
from PIL import Image
from typing import Dict
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
model_client = w.serving_endpoints.get_open_ai_client()

st.header(body="AI / ML", divider=True)
st.subheader("Invoke a multi-modal LLM")
st.markdown(
    "Upload an image and provide a prompt for multi-modal inference, e.g., with [Claude Sonnet 3.7](https://www.databricks.com/blog/anthropic-claude-37-sonnet-now-natively-available-databricks)."
)

tab1, tab2, tab3 = st.tabs(
    ["**Try it**", "**Code snippet**", "**Requirements**"])


def pillow_image_to_base64_string(image):
    """Convert a Pillow image to a base64-encoded string for API transmission."""
    buffered = io.BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def chat_with_mllm(endpoint_name,
                   prompt,
                   image,
                   messages=None) -> tuple[str, Dict]:
    """
    Chat with a multi-modal LLM using Mosaic AI Model Serving.
    
    This function sends the prompt and image(s) to, e.g., a Claude Sonnet 3.7 endpoint
    using Databricks SDK.
    """

    image_data = pillow_image_to_base64_string(image)
    messages = messages or []

    current_user_message = {
        "role":
        "user",
        "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                },
            },
        ],
    }
    messages.append(current_user_message)

    completion = model_client.chat.completions.create(
        model=endpoint_name,
        messages=messages,
    )
    completion_text = completion.choices[0].message.content

    messages.append({
        "role": "assistant",
        "content": [{
            "type": "text",
            "text": completion_text
        }]
    })

    return completion_text, messages


with tab1:
    endpoints = w.serving_endpoints.list()
    endpoint_names = [endpoint.name for endpoint in endpoints]

    selected_model = st.selectbox("Select a multi-modal Model Serving endpoint",
                                  endpoint_names)

    uploaded_file = st.file_uploader("Select an image (JPG, JPEG, or PNG)",
                                     type=["jpg", "jpeg", "png"])

    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="Describe or ask something about the image...",
        value="Describe the image(s) as an alternative text",
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded image")

    if st.button("Invoke LLM"):
        if uploaded_file:
            with st.spinner("Processing..."):
                completion_text, _ = chat_with_mllm(
                    endpoint_name=selected_model,
                    prompt=prompt,
                    image=image,
                )

            st.write(completion_text)
        else:
            st.error("Please upload an image to proceed.")

with tab2:
    st.code("""
import io
import base64
import streamlit as st
from PIL import Image
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
model_client = w.serving_endpoints.get_open_ai_client()


def pillow_image_to_base64_string(image):
    buffered = io.BytesIO()
    image.convert("RGB").save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def chat_with_mllm(endpoint_name, prompt, image):
    image_data = pillow_image_to_base64_string(image)
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
        ],
    }]
    completion = model_client.chat.completions.create(
        model=endpoint_name,
        messages=messages,
    )

    return completion.choices[0].message.content

# UI elements
endpoints = w.serving_endpoints.list()
endpoint_names = [endpoint.name for endpoint in endpoints]

selected_model = st.selectbox("Select a model served by Model Serving", endpoint_names)
uploaded_file = st.file_uploader("Select an image", type=["jpg", "jpeg", "png"])
prompt = st.text_area("Enter your prompt:")

if st.button("Invoke LLM"):
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded image")
        with st.spinner("Processing..."):
            result = chat_with_mllm(selected_model, prompt, image)
        st.write(result)
    """)

with tab3:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `CAN QUERY` on the model serving endpoint
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Multi-modal Model Serving endpoint
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
