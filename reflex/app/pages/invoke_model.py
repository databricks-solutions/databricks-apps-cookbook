import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.states.invoke_model_state import InvokeModelState
from app import theme


def _pattern_accordion(title: str, description: str, code: str) -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            rx.accordion.header(
                rx.accordion.trigger(
                    rx.hstack(
                        rx.text(title, class_name="font-medium"),
                        rx.icon("chevron-down", class_name="h-4 w-4"),
                        justify="between",
                        width="100%",
                        align="center",
                    ),
                    class_name="flex items-center w-full px-4 py-2 text-sm font-semibold rounded-lg transition-colors",
                    color="white",
                    background_color="#3B82F6",
                    _hover={
                        "background_color": theme.ACTIVE_ITEM_BG,
                        "color": theme.ACTIVE_ITEM_TEXT,
                    },
                )
            ),
            rx.accordion.content(
                rx.vstack(
                    rx.text(description, class_name="font-semibold text-gray-700 mb-2"),
                    rx.code_block(code, language="python", width="100%"),
                    spacing="2",
                    width="100%",
                    padding="4",
                )
            ),
            value="item-1",
            style={
                "background_color": "white",
                "border": "1px solid #E5E7EB",
                "border_radius": "0.5rem",
            },
        ),
        type="single",
        collapsible=True,
        width="100%",
        class_name="mb-2",
    )


def invoke_model_code_display() -> rx.Component:
    """The code snippet content for the Invoke Model page, using an accordion."""
    return rx.vstack(
        _pattern_accordion(
            "Traditional Models (e.g., scikit-learn, XGBoost) (dataframe_split)",
            "Pattern 1: dataframe_split (Pandas DataFrame)",
            """
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import DataframeSplitInput
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="traditional-model",
    dataframe_split={
        "columns": ["feature1", "feature2"],
        "data": [[1, 2], [3, 4]]
    }
)
rx.text(response.as_dict())
""",
        ),
        _pattern_accordion(
            "Traditional Models (dataframe_records)",
            "Pattern 2: dataframe_records (List of Dicts)",
            """
from databricks.sdk import WorkspaceClient
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="traditional-model",
    dataframe_records=[
        {"feature1": 1, "feature2": 2},
        {"feature1": 3, "feature2": 4}
    ]
)
rx.text(response.as_dict())
""",
        ),
        _pattern_accordion(
            "TensorFlow and PyTorch Models (instances)",
            "Pattern 3: instances (Tensor-based input)",
            """
from databricks.sdk import WorkspaceClient
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="tf-model",
    instances=[
        [1, 2], [3, 4]
    ]
)
rx.text(response.as_dict())
""",
        ),
        _pattern_accordion(
            "TensorFlow and PyTorch Models (inputs)",
            "Pattern 4: inputs (Dict-based input)",
            """
from databricks.sdk import WorkspaceClient
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="pytorch-model",
    inputs={"input_ids": [1, 2, 3]}
)
rx.text(response.as_dict())
""",
        ),
        _pattern_accordion(
            "Completions Models (prompt)",
            "Pattern 5: prompt (Text Completion)",
            """
from databricks.sdk import WorkspaceClient
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="completion-model",
    prompt="Once upon a time"
)
rx.text(response.as_dict())
""",
        ),
        _pattern_accordion(
            "Chat Models (messages)",
            "Pattern 6: messages (Chat Completion)",
            """
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="chat-model",
    messages=[
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"}
    ]
)
rx.text(response.as_dict())
""",
        ),
        _pattern_accordion(
            "Embeddings Models (input)",
            "Pattern 7: input (Embeddings)",
            """
from databricks.sdk import WorkspaceClient
import reflex as rx

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="embeddings-model",
    input=["text to embed"]
)
rx.text(response.as_dict())
""",
        ),
        rx.box(
            rx.markdown(
                """
### Extensions

* [Gradio](https://gradio.app/guides/quickstart) - Enable ML prototyping with pre-built interactive components for models involving images, audio, or video.
* [Dash](https://plotly.com/examples/) - Build interactive, data-rich visualizations to explore and analyze the behavior of your ML models in depth.
* [Shiny](https://shiny.posit.co/blog/posts/shiny-python-chatstream/) - Build AI chat apps.
* [LangChain on Databricks](https://docs.databricks.com/en/large-language-models/langchain.html) - Excels at chaining LLM calls, integration with external APIs, and managing conversational contexts.

Also, check out [Databricks Serving Query API](https://docs.databricks.com/api/workspace/servingendpoints/query). It provides the example responses and optional arguments for the above Implement cases.
""",
                class_name="text-sm text-gray-600 [&_a]:text-blue-600 [&_a]:hover:underline [&_h3]:text-lg [&_h3]:font-semibold [&_h3]:text-gray-900 [&_h3]:mb-2 [&_ul]:list-disc [&_ul]:list-inside [&_ul]:mb-2 [&_li]:mb-1",
            ),
            class_name="mt-4 p-4 border rounded-lg bg-gray-50 border-gray-200 w-full",
        ),
        width="100%",
        spacing="4",
    )


def invoke_model_requirements() -> rx.Component:
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
            rx.markdown("* Model serving endpoint", class_name="text-sm text-gray-600"),
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


def invoke_model_content() -> rx.Component:
    """Content for the 'Try It' tab of the Invoke Model page."""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Model Name", class_name="font-semibold text-sm"),
                rx.select(
                    InvokeModelState.endpoint_names,
                    value=InvokeModelState.selected_model,
                    on_change=InvokeModelState.set_selected_model,
                    placeholder="Select a model...",
                    class_name="w-full",
                ),
                width="70%",
            ),
            rx.vstack(
                rx.text("Model Type", class_name="font-semibold text-sm"),
                rx.select(
                    ["LLM", "Traditional ML"],
                    value=InvokeModelState.model_type,
                    on_change=InvokeModelState.set_model_type,
                    class_name="w-full",
                ),
                width="30%",
            ),
            width="100%",
            spacing="4",
            align="start",
        ),
        rx.cond(
            InvokeModelState.model_type == "LLM",
            rx.vstack(
                rx.text("Prompt", class_name="font-semibold text-sm"),
                rx.text_area(
                    placeholder="Ask something...",
                    on_change=InvokeModelState.set_prompt,
                    class_name="w-full h-32",
                    default_value=InvokeModelState.prompt,
                ),
                rx.hstack(
                    rx.text("Temperature", class_name="font-semibold text-sm"),
                    rx.text(
                        InvokeModelState.temperature, class_name="text-sm text-gray-500"
                    ),
                    spacing="2",
                ),
                rx.el.input(
                    type="range",
                    default_value=InvokeModelState.temperature,
                    min="0.0",
                    max="2.0",
                    step="0.1",
                    on_change=InvokeModelState.set_temperature.throttle(100),
                    class_name="w-full",
                    key=InvokeModelState.temperature.to_string(),
                ),
                rx.text(
                    "Controls randomness: Lowering results in less random completions. As the temperature approaches zero, the model will become deterministic and repetitive.",
                    class_name="text-xs text-gray-500",
                ),
                rx.button(
                    "Invoke LLM",
                    on_click=InvokeModelState.invoke_llm,
                    is_loading=InvokeModelState.is_loading,
                    bg=theme.PRIMARY_COLOR,
                    class_name="text-white",
                    _hover={"opacity": 0.8},
                ),
                width="100%",
                spacing="4",
            ),
            rx.vstack(
                rx.box(
                    rx.text(
                        "Ensure your model is deployed using ",
                        rx.code("dataframe_records"),
                        " (list of dictionaries) format and check the model signature for required input fields.",
                        class_name="text-sm",
                    ),
                    class_name="bg-blue-50 border border-blue-200 p-4 rounded-lg text-blue-800 w-full",
                ),
                rx.text("Input (JSON)", class_name="font-semibold text-sm"),
                rx.text_area(
                    placeholder='[{"feature1": 1, "feature2": 2}]',
                    on_change=InvokeModelState.set_input_value,
                    class_name="w-full h-32 font-mono",
                    default_value=InvokeModelState.input_value,
                ),
                rx.button(
                    "Invoke Model",
                    on_click=InvokeModelState.invoke_traditional_ml,
                    is_loading=InvokeModelState.is_loading,
                    bg=theme.PRIMARY_COLOR,
                    class_name="text-white",
                    _hover={"opacity": 0.8},
                ),
                width="100%",
                spacing="4",
            ),
        ),
        rx.cond(
            InvokeModelState.error_message,
            rx.box(
                rx.icon(tag="triangle-alert", class_name="text-red-500 mr-2"),
                rx.text(InvokeModelState.error_message, color="red.500"),
                class_name="flex items-center p-4 bg-red-50 border border-red-200 rounded-lg w-full",
            ),
        ),
        rx.cond(
            InvokeModelState.is_loading,
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Loading...", class_name="text-gray-500"),
                align="center",
                justify="center",
                class_name="w-full h-32 bg-gray-50 rounded-lg",
            ),
        ),
        rx.cond(
            InvokeModelState.response_data,
            rx.vstack(
                rx.text("Response", class_name="font-semibold text-sm"),
                rx.code_block(
                    InvokeModelState.response_data.to_string(),
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        width="100%",
        spacing="4",
        align="start",
    )


def invoke_model_page() -> rx.Component:
    """The Invoke a Model sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Invoke a Model Serving Endpoint",
            page_description="Send requests to a Databricks Model Serving endpoint and display the returned predictions.",
            try_it_content=invoke_model_content,
            code_snippet_content=invoke_model_code_display,
            requirements_content=invoke_model_requirements,
        )
    )