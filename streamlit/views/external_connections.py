import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json


@st.cache_resource
def get_client_obo() -> WorkspaceClient:
    user_token = st.context.headers.get("x-forwarded-access-token")
    if not user_token:
        st.error("User token is required for OBO authentication")
        return None

    if user_token:
        return WorkspaceClient(
            token=user_token, 
            auth_type="pat",
        )


st.header(body="External services", divider=True)
st.subheader("External connections")
st.write(
    "This recipe demonstrates how to use Unity Catalog-managed external HTTP connections for secure and governed access to non-MCP servers, for example, to GitHub, or Jira, and Slack."
)

tab_app, tab_code, tab_config = st.tabs(["Try it", "Code snippet", "Requirements"])

with tab_app:
    st.info(
        "This sample will only work as intended when deployed to Databricks Apps and not when running locally. Also, you need to configure on-behalf-of-user authentication for this Databricks Apps application.",
        icon="ℹ️",
    )

    connection_name = st.text_input("Unity Catalog Connection name:", placeholder="Enter connection name...", help="See [this guide](https://docs.databricks.com/aws/en/query-federation/http)")
    auth_mode = st.radio(
        "Authentication mode:",
        ["OAuth User to Machine Per User (On-behalf-of-user)", "Bearer token", "OAuth Machine to Machine"],
    )
    http_method = st.selectbox("HTTP method:", options=["GET", "POST", "PUT", "DELETE", "PATCH"], )
    path = st.text_input("Path:", placeholder="/api/endpoint")
    request_headers = st.text_area("Request headers:", placeholder='{"Content-Type": "application/json"}') or {}
    request_data = st.text_area("Request data:", placeholder='{"key": "value"}')

    all_fields_filled = path and connection_name
    if not all_fields_filled:
        st.info("Please fill in all required fields to run a query.")

    connection_name = connection_name.replace(" ", "") if connection_name else ""

    if st.button("Send Request"):
        if auth_mode == "Bearer token":
            w = WorkspaceClient()
        elif auth_mode == "OAuth User to Machine Per User (On-behalf-of-user)":
            w = get_client_obo()
        elif auth_mode == "OAuth Machine to Machine":
            # TODO: Add OAuth Machine-to-Machine logic
            w = WorkspaceClient()

        if request_headers and request_headers.strip():
            try:
                request_headers = json.loads(request_headers)
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON in headers")
        
        if request_data and request_data.strip():
            try:
                request_data = json.loads(request_data) if request_data else json.loads(None)
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON data")

        http_method = getattr(ExternalFunctionRequestHttpMethod, http_method)

        response = w.serving_endpoints.http_request(
            conn=connection_name, 
            method=http_method, 
            path=path, 
            headers=request_headers if request_headers else None,
            json=request_data if request_data else {},
        )
        st.subheader("Response")
        st.json(response.json())



with tab_code:
    table = [
        {
            "type": "OAuth User to Machine Per User (On-behalf-of-user)",
            "code": """
            ```python
            import streamlit as st
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
            import json
 
            
            token = st.context.headers.get("x-forwarded-access-token")
            w = WorkspaceClient(token=token, auth_type="pat")
            

            def init_mcp_session(w: WorkspaceClient, connection_name: str):
                init_payload = {
                    "jsonrpc": "2.0",
                    "id": "init-1",
                    "method": "initialize",
                    "params": {}
                }
                response = w.serving_endpoints.http_request(
                    conn=connection_name,
                    method=ExternalFunctionRequestHttpMethod.POST,
                    path="/",
                    json=init_payload,
                )
                return response.headers.get("mcp-session-id")


            connection_name = "github_u2m_connection"
            http_method = ExternalFunctionRequestHttpMethod.POST
            path = "/"
            headers = {"Content-Type": "application/json"}
            payload = {"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}

            if st.button("Run"):
                session_id = init_mcp_session(w, connection_name)
                headers["Mcp-Session-Id"] = session_id

                response = w.serving_endpoints.http_request(
                    conn=connection_name,
                    method=http_method,
                    path=path,
                    headers=headers,
                    json=payload,
                )
                st.json(response.json())
            ```
            """,
        },
        {
            "type": "Bearer token",
            "code": """
            ```python
            import streamlit as st
            from databricks.sdk import WorkspaceClient
            from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

            w = WorkspaceClient()

            response = w.serving_endpoints.http_request(
                conn="github_connection",
                method=ExternalFunctionRequestHttpMethod.GET,
                path="/traffic/views",
                headers={"Accept": "application/vnd.github+json"},
            )

            st.json(response.json())
            ```
            """,
        }
    ]

    for i, row in enumerate(table):
        with st.expander(f"**{row['type']}**", expanded=(i == 0)):
            st.markdown(row["code"])


with tab_config:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (user or app service principal)**
                    * `USE CONNECTION` permission on the HTTP Connection
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * [Unity Catalog HTTP Connection](https://docs.databricks.com/aws/en/query-federation/http)
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
