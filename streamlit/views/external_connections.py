import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
import json
import re


@st.cache_resource
def get_client_obo() -> WorkspaceClient:
    user_token = st.context.headers["X-Forwarded-Access-Token"]
    if not user_token:
        st.error("User token is required for OBO authentication")
        return None

    if user_token:
        return WorkspaceClient(
            token=user_token, 
            auth_type="pat"
        )
    

def init_github_mcp_connection(w: WorkspaceClient, uc_connection_name: str):
    """Initialize GitHub MCP and get session ID"""
    st.session_state.mcp_session_id = None
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


HTTP_METHODS = [
    {"label": "GET", "value": "GET"},
    {"label": "POST", "value": "POST"}
]

AUTH_TYPES = [
    {"label": "Bearer token", "value": "bearer_token"},
    {"label": "OAuth User to Machine Per User", "value": "oauth_user_machine_per_user"},
    {"label": "OAuth Machine to Machine", "value": "oauth_machine_machine"}
]


st.header(body="External connections", divider=True)
st.subheader("Securely call external API services")
st.write(
    "This recipe demonstrates how to use Unity Catalog-managed external HTTP connections for secure and governed access, for example, to GitHub, Jira, and Slack."
)

tab_app, tab_code, tab_config = st.tabs(["Try it", "Code snippet", "Requirements"])

with tab_app:
    st.info(
        "This sample will only work as intended when deployed to Databricks Apps and not when running locally. Also, you need to configure on-behalf-of-user authentication for this Databricks Apps application.",
        icon="ℹ️",
    )

    connection_name = st.text_input("Connection Name", placeholder="Enter connection name...")
    auth_mode = st.radio(
        "Authentication Mode:",
        ["Bearer token", "OAuth User to Machine Per User", "OAuth Machine to Machine"],
        help="Bearer token is the user token.",
    )
    http_method = st.selectbox("HTTP Method", options=["GET", "POST", "PUT", "DELETE", "PATCH"], )
    path = st.text_input("Path", placeholder="/api/endpoint")
    request_type = st.selectbox("Request Type", options=["Non-MCP", "MCP"])
    request_headers = st.text_area("Request headers", value='{"Content-Type": "application/json"}')
    request_data = st.text_area("Request data", value='{"key": "value"}')

    all_fields_filled = path and connection_name != ""
    if not all_fields_filled:
        st.info("Please fill in all required fields to run a query.")


    if st.button("Send Request"):
        if auth_mode == "Bearer token":
            w = WorkspaceClient()
        elif auth_mode == "OAuth User to Machine Per User":
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
                request_data = json.loads(request_data)
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON data")

        http_method = getattr(ExternalFunctionRequestHttpMethod, http_method)

        if request_type == "MCP":
            if not st.session_state.mcp_session_id:
                session_id, error = init_github_mcp_connection(w)
                if error:
                    if is_connection_login_error(error):
                        login_url = extract_login_url_from_error(error)
                        if login_url:
                            st.warning("🔐 Connection Login Required")
                            st.markdown("You need to authenticate with the external connection first.")
                            st.markdown(f"[Login to Connection]({login_url})")
                        else:
                            st.error("❌ MCP error: {error}")
                    else:
                        st.error("❌ MCP initialization error: {error}")

                st.session_state.mcp_session_id = session_id
            
            request_headers["Mcp-Session-Id"] = st.session_state.mcp_session_id

        response = w.serving_endpoints.http_request(
            conn=connection_name, 
            method=http_method, 
            path=path, 
            headers=request_headers,
            json=request_data,
        )
        st.subheader("Response")
        st.json(response.json())



with tab_code:
    st.code("""
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

def get_user_token():
    headers = st.context.headers
    user_token = headers["X-Forwarded-Access-Token"]
    return user_token

@st.cache_resource
def connect_with_obo(http_path, user_token):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        access_token=user_token
    )

def execute_query(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name} LIMIT 10"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

user_token = get_user_token()

http_path = "/sql/1.0/warehouses/abcd1234"
table_name = "samples.nyctaxi.trips"

if st.button("Run Query"):
    conn = connect_with_obo(http_path, user_token)
    
    df = execute_query(table_name, conn)
    st.dataframe(df)
""")

with tab_config:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (user or app service principal)**
                    * `SELECT` permissions on the tables being queried
                    * `CAN USE` on the SQL warehouse
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * SQL warehouse
                    * Unity Catalog table
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
