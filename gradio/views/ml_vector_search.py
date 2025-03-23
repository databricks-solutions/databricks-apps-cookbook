import gradio as gr
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
openai_client = w.serving_endpoints.get_open_ai_client()

EMBEDDING_MODEL_ENDPOINT_NAME = "databricks-gte-large-en"

def get_embeddings(text):
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_ENDPOINT_NAME, input=text
        )
        return response.data[0].embedding
    except Exception as e:
        return f"Error generating embeddings: {e}"

def run_vector_search(index_name: str, columns: str, query: str) -> str:
    if not all([index_name, columns, query]):
        return "Please fill in all fields"
    
    prompt_vector = get_embeddings(query)
    if isinstance(prompt_vector, str):
        return f"Failed to generate embeddings: {prompt_vector}"

    columns_to_fetch = [col.strip() for col in columns.split(",") if col.strip()]

    try:
        query_result = w.vector_search_indexes.query_index(
            index_name=index_name,
            columns=columns_to_fetch,
            query_vector=prompt_vector,
            num_results=3,
        )
        return str(query_result.result.data_array)
    except Exception as e:
        return f"Error during vector search: {e}"

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# AI / ML")
    gr.Markdown("## Run vector search")
    gr.Markdown("This recipe uses vector search for fast and accurate retrieval of the most similar items or content.")
    
    with gr.Tab("Try it"):
        index_input = gr.Textbox(
            label="Vector search index",
            placeholder="catalog.schema.index-name"
        )
        columns_input = gr.Textbox(
            label="Columns to retrieve (comma-separated)",
            placeholder="url, name",
            info="Enter one or more column names present in the vector search index, separated by commas. E.g. id, text, url."
        )
        query_input = gr.Textbox(
            label="Your query",
            placeholder="What is Databricks?"
        )
        search_button = gr.Button("Run vector search")
        output = gr.Textbox(label="Search results")
        
        search_button.click(
            fn=run_vector_search,
            inputs=[index_input, columns_input, query_input],
            outputs=output
        )
    
    with gr.Tab("Requirements"):
        gr.Markdown("""
        **Permissions (app service principal)**
        * `USE CATALOG` on the Catalog that contains the Vector Search index
        * `USE SCHEMA` on the Schema that contains the Vector Search index
        * `SELECT` on the Vector Search index
        
        **Databricks resources**
        * Vector Search endpoint
        * Vector Search index
        
        **Dependencies**
        * [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
        * [Gradio](https://pypi.org/project/gradio/) - `gradio`
        """)

if __name__ == "__main__":
    demo.launch()