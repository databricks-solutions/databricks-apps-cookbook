import streamlit as st
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

st.header(body="AI / ML", divider=True)
st.subheader("Run vector search")
st.write(
    "This recipe uses vector search for fast and accurate retrieval of the most similar items or content."
)

tab1, tab2, tab3 = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

openai_client = w.serving_endpoints.get_open_ai_client()

EMBEDDING_MODEL_ENDPOINT_NAME = "databricks-gte-large-en"

def get_embeddings(text):
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_ENDPOINT_NAME, input=text
        )
        return response.data[0].embedding
    except Exception as e:
        st.text(f"Error generating embeddings: {e}")


def run_vector_search(prompt: str) -> str:
    prompt_vector = get_embeddings(prompt)
    if prompt_vector is None or isinstance(prompt_vector, str):
        return f"Failed to generate embeddings: {prompt_vector}"

    columns_to_fetch = [col.strip() for col in columns.split(",") if col.strip()]

    try:
        query_result = w.vector_search_indexes.query_index(
            index_name=index_name,
            columns=columns_to_fetch,
            query_vector=prompt_vector,
            num_results=3,
        )
        return query_result.result.data_array
    except Exception as e:
        return f"Error during vector search: {e}"


with tab1:
    index_name = st.text_input(
        label="Vector search index:",
        placeholder="catalog.schema.index-name",
    )

    columns = st.text_input(
        label="Columns to retrieve (comma-separated):",
        placeholder="url, name",
        help="Enter one or more column names present in the vector search index, separated by commas. E.g. id, text, url.",
    )

    text_input = st.text_input(
        label="Your query:",
        placeholder="What is Databricks?",
        key="search_query_key",
    )

    if st.button("Run vector search"):
        result = run_vector_search(text_input)
        st.write("Search results:")
        st.write(result)


with tab2:
    st.code("""
    import streamlit as st
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
            st.text(f"Error generating embeddings: {e}")


    def run_vector_search(prompt: str) -> str:
        prompt_vector = get_embeddings(prompt)
        if prompt_vector is None or isinstance(prompt_vector, str):
            return f"Failed to generate embeddings: {prompt_vector}"

        columns_to_fetch = [col.strip() for col in columns.split(",") if col.strip()]

        try:
            query_result = w.vector_search_indexes.query_index(
                index_name=index_name,
                columns=columns_to_fetch,
                query_vector=prompt_vector,
                num_results=3,
            )
            return query_result.result.data_array
        except Exception as e:
            return f"Error during vector search: {e}"


    index_name = st.text_input(
        label="Unity Catalog Vector search index:",
        placeholder="catalog.schema.index-name",
    )

    columns = st.text_input(
        label="Columns to retrieve (comma-separated):",
        placeholder="url, name",
        help="Enter one or more column names present in the vector search index, separated by commas. E.g. id, text, url.",
    )

    text_input = st.text_input(
        label="Enter your search query:",
        placeholder="What is Databricks?",
        key="search_query_key",
    )

    if st.button("Run vector search"):
        result = run_vector_search(text_input)
        st.write("Search results:")
        st.write(result)
    """)

with tab3:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `USE CATALOG` on the Catalog that contains the Vector Search index
                    * `USE SCHEMA` on the Schema that contains the Vector Search index
                    * `SELECT` on the Vector Search index
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Vector Search endpoint
                    * Vector Search index
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK for Python](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
