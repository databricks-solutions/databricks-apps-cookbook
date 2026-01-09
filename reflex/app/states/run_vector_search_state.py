import reflex as rx
from databricks.sdk import WorkspaceClient
import asyncio
import logging


def get_embeddings(text: str):
    try:
        w = WorkspaceClient()
        openai_client = w.serving_endpoints.get_open_ai_client()
        EMBEDDING_MODEL_ENDPOINT_NAME = "databricks-gte-large-en"
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_ENDPOINT_NAME, input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logging.exception(f"Error generating embeddings: {e}")
        return f"Error generating embeddings: {e}"


def run_vector_search(index_name: str, columns: str, prompt: str):
    columns_list = [col.strip() for col in columns.split(",") if col.strip()]
    prompt_vector = get_embeddings(prompt)
    if prompt_vector is None or isinstance(prompt_vector, str):
        return {"error": str(prompt_vector)}
    try:
        w = WorkspaceClient()
        results = w.vector_search_indexes.query_index(
            index_name=index_name,
            columns=columns_list,
            query_vector=prompt_vector,
            num_results=3,
        )
        return results.result.data_array
    except Exception as e:
        logging.exception(f"Error running vector search: {e}")
        return {"error": f"Error running vector search: {e}"}


class RunVectorSearchState(rx.State):
    """State for the Run Vector Search page."""

    index_name: str = ""
    columns: str = ""
    search_query: str = ""
    search_results: str = ""
    is_searching: bool = False

    @rx.event(background=True)
    async def perform_search(self):
        async with self:
            self.is_searching = True
            self.search_results = ""
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                run_vector_search,
                self.index_name,
                self.columns,
                self.search_query,
            )
            async with self:
                self.search_results = str(result)
        except Exception as e:
            logging.exception(f"Error running vector search: {e}")
            async with self:
                self.search_results = f"Error: {e}"
        finally:
            async with self:
                self.is_searching = False