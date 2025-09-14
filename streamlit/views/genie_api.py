from typing import Dict

import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieMessage

import streamlit as st

w = WorkspaceClient()

st.header("Business Intelligence", divider=True)
st.subheader("Genie - Converse with your data")
st.write(
    """
    This app uses [Genie](https://www.databricks.com/product/ai-bi) [API](https://docs.databricks.com/api/workspace/genie) 
    to let users ask questions about your data for instant insights.
    """
)

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:

    def reset_conversation():
        st.session_state.conversation_id = None
        st.session_state.messages = []

    genie_space_id = st.text_input(
        "Genie Space ID",
        placeholder="01efe16a65e21836acefb797ae6a8fe4",
        help="Room ID in the Genie Space URL",
    )
    if genie_space_id != st.session_state.get("genie_space_id", ""):
        reset_conversation()
        st.session_state.genie_space_id = genie_space_id

    def display_message(message: Dict):
        if "content" in message:
            st.markdown(message["content"])
        if "data" in message:
            st.dataframe(message["data"])
        if "code" in message:
            with st.expander("Show generated code"):
                st.code(message["code"], language="sql", wrap_lines=True)

    def get_query_result(statement_id: str) -> pd.DataFrame:
        query = w.statement_execution.get_statement(statement_id)
        result = query.result.data_array

        next_chunk = query.result.next_chunk_index
        while next_chunk:
            chunk = w.statement_execution.get_statement_result_chunk_n(
                statement_id, next_chunk
            )
            result.append(chunk.data_array)
            next_chunk = chunk.next_chunk_index

        return pd.DataFrame(
            result, columns=[i.name for i in query.manifest.schema.columns]
        )

    def process_genie_response(response: GenieMessage):
        st.session_state.conversation_id = response.conversation_id

        for i in response.attachments:
            if i.text:
                message = {"role": "assistant", "content": i.text.content}
                display_message(message)
                st.session_state.messages.append(message)
            elif i.query:
                data = get_query_result(response.query_result.statement_id)
                message = {
                    "role": "assistant",
                    "content": i.query.description,
                    "data": data,
                    "code": i.query.query,
                }
                display_message(message)
                st.session_state.messages.append(message)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            display_message(message)

    if prompt := st.chat_input("Ask your question..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if genie_space_id:
                status = st.status("Thinking")
                if st.session_state.get("conversation_id"):
                    try:
                        conversation = w.genie.create_message_and_wait(
                            genie_space_id, st.session_state.conversation_id, prompt
                        )
                    except Exception as e:
                        status.update(
                            label="Conversation failed. Check the required permissions.",
                            state="error",
                        )
                        st.button("New Chat", on_click=reset_conversation)
                        raise e
                    if conversation.error:
                        st.error(conversation.error.type, conversation.error.error)
                    process_genie_response(conversation)
                else:
                    try:
                        conversation = w.genie.start_conversation_and_wait(
                            genie_space_id, prompt
                        )
                    except Exception as e:
                        status.update(
                            label="Failed to initialize Genie. Check the required permissions.",
                            state="error",
                        )
                        st.button("New Chat", on_click=reset_conversation)
                        raise e
                    if conversation.error:
                        st.error(conversation.error.type, conversation.error.error)
                    process_genie_response(conversation)
                status.update(label="", state="complete")
                st.button("New Chat", on_click=reset_conversation)
                st.link_button(
                    "Open Genie",
                    f"{w.config.host}/genie/rooms/{genie_space_id}/chats/{st.session_state.conversation_id}",
                )
            else:
                st.error("Please fill in the Genie Space ID.")


with tab_b:
    st.markdown("Refer to the source code for the full implmenetation.")
    st.code(
        """
import streamlit as st
from databricks.sdk import WorkspaceClient
import pandas as pd

w = WorkspaceClient()

genie_space_id = "01f0023d28a71e599b5a62f4117916d4"


def display_message(message):
    if "content" in message:
        st.markdown(message["content"])
    if "data" in message:
        st.dataframe(message["data"])
    if "code" in message:
        with st.expander("Show generated code"):
            st.code(message["code"], language="sql", wrap_lines=True)

            
def get_query_result(statement_id):
    # For simplicity, let's say data fits in one chunk, query.manifest.total_chunk_count = 1

    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array, columns=[i.name for i in result.manifest.schema.columns]
    )

    
def process_genie_response(response):
    for i in response.attachments:
        if i.text:
            message = {"role": "assistant", "content": i.text.content}
            display_message(message)
        elif i.query:
            data = get_query_result(response.query_result.statement_id)
            message = {
                "role": "assistant", "content": i.query.description, "data": data, "code": i.query.query
            }
            display_message(message)
            

if prompt := st.chat_input("Ask your question..."):
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        if st.session_state.get("conversation_id"):
            conversation = w.genie.create_message_and_wait(
                genie_space_id, st.session_state.conversation_id, prompt
            )
            process_genie_response(conversation)
        else:
            conversation = w.genie.start_conversation_and_wait(genie_space_id, prompt)
            process_genie_response(conversation)
        """
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            **Permissions (app service principal)**
            * `SELECT` on the Unity Catalog table
            * `CAN USE` the SQL warehouse
            * `CAN VIEW` the Genie Space
            """
        )

    with col2:
        st.markdown(
            """
            **Databricks resources**
            * Genie API
            """
        )

    with col3:
        st.markdown(
            """
            **Dependencies**
            * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
            * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
            * [Pandas](https://pypi.org/project/pandas/) - `pandas`
            """
        )
