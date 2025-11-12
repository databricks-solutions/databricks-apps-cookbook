import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json
import re


if "mcp_session_id" not in st.session_state:
    st.session_state.mcp_session_id = None


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
    

def init_github_mcp_connection(w: WorkspaceClient, uc_connection_name: str):
    """Initialize GitHub MCP and get session ID"""
    try:
        init_json = {
            "jsonrpc": "2.0",
            "id": "init-1",
            "method": "initialize",
            "params": {}
        }
        
        response = w.serving_endpoints.http_request(
            conn=uc_connection_name,
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            json=init_json,
        )
        
        session_id = response.headers.get("mcp-session-id")
        if session_id:
            st.session_state.mcp_session_id = session_id
            return session_id, None
        
        else:
            return None, "No session ID returned by server"
            
    except Exception as e:
        return None, f"Error initializing MCP: {str(e)}"
    

def extract_login_url_from_error(error: str):
    """Extract login URL from error message"""

    url_pattern = r'https://[^\s]+/explore/connections/[^\s]+'
    match = re.search(url_pattern, error)

    if match:
        return match.group(0)
    
    return None


def is_connection_login_error(error: str):
    """Check if error is a connection login error"""
    return "Credential for user identity" in error and "Please login first to the connection" in error


st.header(body="AI / ML", divider=True)
st.subheader("Connect an MCP server")
st.write(
    "This recipe connects to an [MCP](https://modelcontextprotocol.io/overview) server for AI applications using GitHub as an example and the Unity Catalog HTTP connection for secure and governed access."
)

tab_app, tab_code, tab_config = st.tabs(["Try it", "Code snippet", "Requirements"])

with tab_app:
    st.info(
        "This sample will only work as intended when deployed to Databricks Apps and not when running locally. Also, you need to configure on-behalf-of-user authentication for this Databricks Apps application.",
        icon="ℹ️",
    )

    connection_name = st.text_input("Unity Catalog Connection name:", placeholder="github_mcp_oauth", help="See [this guide](https://docs.databricks.com/aws/en/query-federation/http)")
    auth_mode = st.radio(
        "Authentication mode:",
        ["OAuth User to Machine Per User (On-behalf-of-user)", "Bearer token", "OAuth Machine to Machine"],
    )
    http_method = st.selectbox("HTTP method:", options=["POST", "GET", "PUT", "DELETE", "PATCH"], )
    request_data = st.text_area("Request data:", value='{"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"}')

    all_fields_filled = connection_name != ""
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

        request_headers = {"Content-Type": "application/json"}
        
        if request_data and request_data.strip():
            try:
                request_data = json.loads(request_data) if request_data else json.loads(None)
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON data")

        http_method = getattr(ExternalFunctionRequestHttpMethod, http_method)

        if not st.session_state.mcp_session_id:
            session_id, error = init_github_mcp_connection(w, connection_name)
            if error:
                if is_connection_login_error(error):
                    login_url = extract_login_url_from_error(error)
                    if login_url:
                        st.warning("🔐 Connection Login Required")
                        st.markdown("You need to authenticate with the external connection first.")
                        st.markdown(f"[Login to Connection]({login_url})")
                    else:
                        st.error(f"❌ MCP error: {error}")
                else:
                    st.error(f"❌ MCP initialization error: {error}")

            st.write("MCP session id", session_id)

            st.session_state.mcp_session_id = session_id
        
        request_headers["Mcp-Session-Id"] = st.session_state.mcp_session_id

        response = w.serving_endpoints.http_request(
            conn=connection_name, 
            method=http_method,
            path="/",
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

            if st.button("Send request"):
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
                conn="github_u2m_connection",
                method=ExternalFunctionRequestHttpMethod.GET,
                path="/",
                headers={"Accept": "application/vnd.github+json"},
                json={
                    "jsonrpc": "2.0",
                    "id": "init-1",
                    "method": "initialize",
                    "params": {}
                },
            )

            st.json(response.json())
            ```
            """,
        },
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
                    * [Unity Catalog HTTP Connection](https://docs.databricks.com/aws/en/query-federation/http) with the MCP (/mcp) base path
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    * [MCP CLI](https://pypi.org/project/mcp/) - `mcp[cli]`
                    """)
