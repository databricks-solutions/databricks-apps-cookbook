import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
from streamlit.web.server.websocket_headers import _get_websocket_headers

cfg = Config()

w = WorkspaceClient()


def get_user_token():
    headers = st.context.headers
    user_token = headers["X-Forwarded-Access-Token"]
    return user_token


@st.cache_resource
def get_connection_obo(http_path, user_token):
    if not user_token:
        st.error("User token is required for OBO authentication")
        return None

    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        access_token=user_token,  # Use the user's token instead of service principal
    )


@st.cache_resource
def get_connection_service_principal(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name} LIMIT 10"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()


def get_schema_names(catalog_name):
    schemas = w.schemas.list(catalog_name=catalog_name)
    return [schema.name for schema in schemas]


def get_table_names(catalog_name, schema_name):
    tables = w.tables.list(catalog_name=catalog_name, schema_name=schema_name)
    return [table.name for table in tables]


st.header(body="Users", divider=True)
st.subheader("On-behalf-of-user authentication")
st.write(
    "This recipe demonstrates how to use Databricks Apps [on-behalf-of-user authentication](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development#-using-the-databricks-apps-authorization-model) to run a SQL query using the user's credentials."
)

tab_app, tab_code, tab_config = st.tabs(["Try it", "Code snippet", "Requirements"])

with tab_app:
    st.info(
        "This sample will only work as intended when deployed to Databricks Apps and not when running locally. Also, you need to configure on-behalf-of-user authentication for this Databricks Apps application.",
        icon="ℹ️",
    )

    try:
        warehouses = w.warehouses.list()
        warehouse_paths = {wh.name: wh.odbc_params.path for wh in warehouses}
        http_path_input = st.selectbox(
            "Select a SQL warehouse:", [""] + list(warehouse_paths.keys())
        )
    except Exception as e:
        st.error(f"Error listing warehouses: {e}")
        warehouses = []
        warehouse_paths = {}
        http_path_input = st.text_input(
            "Enter Databricks HTTP Path:", placeholder="/sql/1.0/warehouses/xxxxxx"
        )

    try:
        catalogs = w.catalogs.list()
        catalog_name = st.selectbox(
            "Select a catalog:", [""] + [catalog.name for catalog in catalogs]
        )
    except Exception as e:
        st.error(f"Error listing catalogs: {e}")
        catalogs = []
        catalog_name = st.text_input("Enter catalog name:")

    if catalog_name and catalog_name != "":
        try:
            schema_names = get_schema_names(catalog_name)
            schema_name = st.selectbox("Select a schema:", [""] + schema_names)
        except Exception as e:
            st.error(f"Error listing schemas: {e}")
            schema_name = st.text_input("Enter schema name:")
    else:
        schema_name = ""

    if catalog_name and catalog_name != "" and schema_name and schema_name != "":
        try:
            table_names = get_table_names(catalog_name, schema_name)
            table_name = st.selectbox("Select a table:", [""] + table_names)
        except Exception as e:
            st.error(f"Error listing tables: {e}")
            table_name = st.text_input("Enter table name:")
    else:
        table_name = ""

    auth_mode = st.radio(
        "Authentication Mode:",
        ["On-behalf-of-user (OBO)", "Service principal"],
        help="OBO uses the end-user's credentials. Service Principal uses the app's identity.",
    )

    all_fields_filled = http_path_input and table_name and table_name != ""

    run_query = st.button("Run query", disabled=not all_fields_filled)

    if not all_fields_filled:
        st.info("Please fill in all required fields to run a query.")

    http_path = ""
    full_table_name = ""
    if all_fields_filled:
        if http_path_input in warehouse_paths:
            http_path = warehouse_paths[http_path_input]
        else:
            http_path = http_path_input
        full_table_name = f"{catalog_name}.{schema_name}.{table_name}"

    if run_query:
        try:
            user_token = get_user_token()

            with st.spinner("Connecting to Databricks..."):
                if auth_mode == "On-behalf-of-user (OBO)":
                    if not user_token:
                        st.error("User token is required for OBO authentication")
                    else:
                        conn = get_connection_obo(http_path, user_token)
                        st.success("Connected using OBO authentication")
                else:
                    conn = get_connection_service_principal(http_path)
                    st.success("Connected using service principal authentication")

            if conn:
                with st.spinner(f"Querying {full_table_name}..."):
                    df = read_table(full_table_name, conn)
                    if df is not None:
                        st.dataframe(df)
                    else:
                        st.error("No data returned")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info(
                "If using OBO, verify the user token has necessary permissions for this resource"
            )

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
