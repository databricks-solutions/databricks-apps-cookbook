import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import (
    tabbed_page_template,
    placeholder_requirements,
)
from app.states.run_vector_search_state import RunVectorSearchState
from app import theme

CODE_SNIPPET = """
import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
openai_client = w.serving_endpoints.get_open_ai_client()
EMBEDDING_MODEL_ENDPOINT_NAME = "databricks-gte-large-en"

def get_embeddings(text: str):
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_ENDPOINT_NAME, input=text
        )
        return response.data[0].embedding
    except Exception as e:
        return f"Error generating embeddings: {e}"

def run_vector_search(index_name: str, columns: str, prompt: str):
    columns_list = [col.strip() for col in columns.split(",") if col.strip()]
    prompt_vector = get_embeddings(prompt)

    if prompt_vector is None or isinstance(prompt_vector, str):
        return str(prompt_vector)

    try:
        results = w.vector_search_indexes.query_index(
            index_name=index_name,
            columns=columns_list,
            query_vector=prompt_vector,
            num_results=3
        )
        return results.result.data_array
    except Exception as e:
        return f"Error running vector search: {e}"

class VectorSearchState(rx.State):
    index_name: str = ""
    columns: str = ""
    search_query: str = ""
    search_results: str = ""
    is_searching: bool = False

    async def perform_search(self):
        self.is_searching = True
        yield
        result = run_vector_search(self.index_name, self.columns, self.search_query)
        self.search_results = str(result)
        self.is_searching = False
"""


def run_vector_search_requirements() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.heading(
                "Permissions (app service principal)",
                size="4",
                class_name="font-semibold text-gray-800",
            ),
            rx.markdown(
                """
* `USE CATALOG` on the catalog of the index
* `USE SCHEMA` on the schema of the index
* `SELECT` on the Vector Search index
""",
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
                """
* Vector Search endpoint
* Vector Search index
""",
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


def run_vector_search_content() -> rx.Component:
    """Content for the 'Try It' tab of the Vector Search page."""
    return rx.vstack(
        rx.vstack(
            rx.text("Vector Search Index", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="catalog.schema.index_name",
                on_change=RunVectorSearchState.set_index_name,
                class_name="w-full",
                default_value=RunVectorSearchState.index_name,
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Columns to Retrieve", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="url, title, content",
                on_change=RunVectorSearchState.set_columns,
                class_name="w-full",
                default_value=RunVectorSearchState.columns,
            ),
            rx.text(
                "Enter column names separated by commas",
                class_name="text-xs text-gray-500",
            ),
            width="100%",
        ),
        rx.vstack(
            rx.text("Search Query", class_name="font-semibold text-sm"),
            rx.input(
                placeholder="What is Databricks?",
                on_change=RunVectorSearchState.set_search_query,
                class_name="w-full",
                default_value=RunVectorSearchState.search_query,
            ),
            width="100%",
        ),
        rx.button(
            "Run Vector Search",
            on_click=RunVectorSearchState.perform_search,
            is_loading=RunVectorSearchState.is_searching,
            bg=theme.PRIMARY_COLOR,
            class_name="text-white w-full mt-4",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            RunVectorSearchState.search_results,
            rx.vstack(
                rx.text("Search Results:", class_name="font-bold mt-4"),
                rx.code_block(
                    RunVectorSearchState.search_results,
                    language="json",
                    class_name="w-full overflow-x-auto",
                ),
                width="100%",
                spacing="2",
            ),
        ),
        spacing="4",
        width="100%",
    )


def run_vector_search_page() -> rx.Component:
    """The Run Vector Search sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="Run Vector Search",
            page_description="Query a Databricks Vector Search index to find the most relevant documents based on semantic similarity.",
            try_it_content=run_vector_search_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=run_vector_search_requirements,
        )
    )