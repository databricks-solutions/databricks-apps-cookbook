from json import loads
import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

w = WorkspaceClient()

st.header(body="AI / ML", divider=True)
st.subheader("Invoke a model")
st.write(
    "This recipe invokes a model hosted on Mosaic AI Model Serving and returns the result. Choose either a traditional ML model or a large language model (LLM)."
)

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippets**", "**Requirements**"])

with tab_a:
    endpoints = w.serving_endpoints.list()
    endpoint_names = [endpoint.name for endpoint in endpoints]

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_model = st.selectbox(
            "Select a model served by Model Serving", endpoint_names
        )
    with col2:
        model_type = st.radio("Model type", ["LLM", "Traditional ML"])

    if model_type == "LLM":
        temperature = st.slider(
            "Select temperature:",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="Controls the randomness of the LLM output. Only applicable for chat/completions queries.",
        )
        prompt = st.text_area("Enter your prompt:", placeholder="Ask something...")
        if st.button("Invoke LLM"):
            response = w.serving_endpoints.query(
                name=selected_model,
                messages=[
                    ChatMessage(
                        role=ChatMessageRole.SYSTEM,
                        content="You are a helpful assistant.",
                    ),
                    ChatMessage(
                        role=ChatMessageRole.USER,
                        content=prompt,
                    ),
                ],
                temperature=temperature,
            )
            st.json(response.as_dict())

    elif model_type == "Traditional ML":
        st.info(
            "The model has to be [deployed](https://docs.databricks.com/en/machine-learning/model-serving/create-manage-serving-endpoints.html#create-an-endpoint) to Mosaic AI Model Serving. Request pattern corresponds to the model signature [registered in Unity Catalog](https://docs.databricks.com/en/machine-learning/manage-model-lifecycle/index.html#train-and-register-unity-catalog-compatible-models)."
        )
        input_value = st.text_area(
            "Enter model input",
            placeholder='{"feature1": [1.5], "feature2": [2.5]}',
        )
        if st.button("Invoke Model"):
            response = w.serving_endpoints.query(
                name=selected_model, dataframe_records=loads(input_value)
            )
            st.write(response.as_dict())

table = [
    {
        "type": "Traditional Models (e.g., scikit-learn, XGBoost)",
        "param": "dataframe_split",
        "description": "JSON-serialized DataFrame in split orientation.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.service.serving import DataframeSplitInput
        import streamlit as st

        w = WorkspaceClient()

        response = w.serving_endpoints.query(
            name="custom-regression-model",
            dataframe_split=DataframeSplitInput.from_dict({
                "columns": ["feature1", "feature2"],
                "data": [[1.5, 2.5]]
            })
        )
        st.json(response.as_dict())
        ```
        """,
    },
    {
        "type": "Traditional Models",
        "param": "dataframe_records",
        "description": "JSON-serialized DataFrame in records orientation.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        import streamlit as st

        w = WorkspaceClient()

        response = w.serving_endpoints.query(
            name="custom-regression-model",
            dataframe_records={
                "feature1": [1.5],
                "feature2": [2.5]
            }
        )
        st.json(response.as_dict())
        ```
        """,
    },
    {
        "type": "TensorFlow and PyTorch Models",
        "param": "instances",
        "description": "Tensor inputs in row format.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        import streamlit as st

        w = WorkspaceClient()

        tensor_input = [[1.0, 2.0, 3.0]]
        response = w.serving_endpoints.query(
            name="tensor-processing-model",
            instances=tensor_input,
        )
        st.json(response.as_dict())
        ```
        """,
    },
    {
        "type": "TensorFlow and PyTorch Models",
        "param": "inputs",
        "description": "Tensor inputs in columnar format.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        import streamlit as st

        w = WorkspaceClient()

        tensor_input = {
            "input1": [1.0, 2.0, 3.0],
            "input2": [4.0, 5.0, 6.0],
        }
        response = w.serving_endpoints.query(
            name="tensor-processing-model",
            inputs=tensor_input,
        )
        st.json(response.as_dict())
        ```
        """,
    },
    {
        "type": "Completions Models",
        "param": "prompt",
        "description": "Input text for completion tasks.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        import streamlit as st

        w = WorkspaceClient()

        response = w.serving_endpoints.query(
            name="llm-text-completions-model",
            prompt="Generate a recipe for building scalable Databricks Apps.",
            temperature=0.5,
        )
        st.json(response.as_dict())
        ```
        """,
    },
    {
        "type": "Chat Models",
        "param": "messages",
        "description": "List of chat messages for conversational models.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        import streamlit as st
        from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

        w = WorkspaceClient()

        response = w.serving_endpoints.query(
            name="chat-assistant-model",
            messages=[
                ChatMessage(
                    role=ChatMessageRole.SYSTEM, 
                    content="You are a helpful assistant.",
                ),
                ChatMessage(
                    role=ChatMessageRole.USER, 
                    content="Provide tips for deploying Databricks Apps.",
                ),
            ],
        )
        st.json(response.as_dict())
        ```
        """,
    },
    {
        "type": "Embeddings Models",
        "param": "input",
        "description": "Input text for embedding tasks.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        import streamlit as st

        w = WorkspaceClient()

        response = w.serving_endpoints.query(
            name="embedding-model",
            input="Databricks provides a unified analytics platform.",
        )
        st.json(response.as_dict())
        ```
        """,
    },
]

with tab_b:
    for i, row in enumerate(table):
        with st.expander(f"**{row['type']} ({row['param']})**", expanded=(i == 0)):
            st.markdown(f"**Description**: {row['description']}")
            st.markdown(row["code"])

    st.info(
        """
        #### Extensions
        - [Gradio](https://gradio.app/guides/quickstart): Enable ML prototyping with pre-built interactive components for models involving images, audio, or video.
        - [Dash](https://plotly.com/examples/): Build interactive, data-rich visualizations to explore and analyze the behavior of your ML models in depth.
        - [Shiny](https://shiny.posit.co/blog/posts/shiny-python-chatstream/): Build AI chat apps.
        - [LangChain on Databricks](https://docs.databricks.com/en/large-language-models/langchain.html): Excels at chaining LLM calls, integration with external APIs, and managing conversational contexts.

        Also, check out [Databricks Serving Query API](https://docs.databricks.com/api/workspace/servingendpoints/query). It provides the example responses and optional arguments for the above *Implement* cases.
    """,
        icon="ℹ️",
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `CAN QUERY` on the model serving endpoint
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Model serving endpoint
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
