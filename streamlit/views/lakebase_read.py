import pandas as pd
import psycopg
from databricks.sdk import WorkspaceClient

import streamlit as st

st.header("Lakebase Postgres database", divider=True)
st.subheader("Read a table")
st.write(
    "This app connects to a [Databricks Lakebase](https://docs.databricks.com/aws/en/oltp/) OLTP database instance and reads the first 100 rows from any table. "
    "Provide the instance name, database, schema, and table name."
)


w = WorkspaceClient()


def get_connection(host: str, database: str, user: str) -> psycopg.Connection:
    """Get a connection to the Lakebase database using OAuth token."""
    token = w.config.oauth_token().access_token

    return psycopg.connect(
        host=host,
        port=5432,
        dbname=database,
        user=user,
        password=token,
        sslmode="require",
    )


def query_df(host: str, database: str, user: str, sql: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a DataFrame."""
    conn = get_connection(host, database, user)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if not cur.description:
                return pd.DataFrame()

            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
            return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()


tab_try, tab_code, tab_reqs = st.tabs(
    ["**Try it**", "**Code snippet**", "**Requirements**"]
)

with tab_try:
    instance_names = [i.name for i in w.database.list_database_instances()]
    instance_name = st.selectbox("Database instance:", instance_names)
    database = st.text_input("Database:", value="databricks_postgres")
    schema = st.text_input("Schema:", value="public")
    table = st.text_input("Table:", value="your_table_name")

    # Get user and host
    user = w.config.client_id or w.current_user.me().user_name
    host = ""
    if instance_name:
        host = w.database.get_database_instance(name=instance_name).read_write_dns

    if st.button("Read table"):
        if not all([instance_name, host, database, schema, table]):
            st.error("Please provide all required fields.")
        else:
            df = query_df(
                host, database, user, f"SELECT * FROM {schema}.{table} LIMIT 100"
            )
            st.dataframe(df, use_container_width=True)
            st.caption(f"Showing first 100 rows from {schema}.{table}")

with tab_code:
    st.code(
        '''import os
import pandas as pd
import psycopg
from databricks.sdk import WorkspaceClient
import streamlit as st


w = WorkspaceClient()


def get_connection(host: str, database: str, user: str) -> psycopg.Connection:
    """Get a connection to the Lakebase database using OAuth token."""
    token = w.config.oauth_token().access_token
    
    return psycopg.connect(
        host=host,
        port=5432,
        dbname=database,
        user=user,
        password=token,
        sslmode="require",
    )


def query_df(host: str, database: str, user: str, sql: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a DataFrame."""
    conn = get_connection(host, database, user)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            if not cur.description:
                return pd.DataFrame()
            
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
            return pd.DataFrame(rows, columns=cols)
    finally:
        conn.close()


# Get connection parameters from environment variables (set by Databricks Apps)
# or fall back to manual configuration
host = os.getenv("PGHOST")
database = os.getenv("PGDATABASE")
user = os.getenv("PGUSER")

if not all([host, database, user]):
    # Manual configuration if environment variables are not set
    instance_name = "your_instance_name"
    database = "databricks_postgres"
    user = w.config.client_id or w.current_user.me().user_name
    host = w.database.get_database_instance(name=instance_name).read_write_dns

# Query table
schema = "public"
table = "your_table_name"
df = query_df(host, database, user, f"SELECT * FROM {schema}.{table} LIMIT 100")
st.dataframe(df)
''',
        language="python",
    )

with tab_reqs:
    st.info(
        "💡 **Tip:** Add your Lakebase instance as an App resource to automatically configure connection parameters via environment variables. "
        "See the [Lakebase resource documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/lakebase) for details."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            **Permissions (app service principal)**
            * Add the Lakebase instance as an [**App resource**](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/lakebase) to automatically configure permissions and environment variables (`PGHOST`, `PGDATABASE`, `PGUSER`, etc.).
            * Alternatively, manually create a Postgres role for the service principal. See [this guide](https://docs.databricks.com/aws/en/oltp/pg-roles?language=PostgreSQL#create-postgres-roles-and-grant-privileges-for-databricks-identities).
            * Example grants for read access:
            """
        )
        st.code(
            """
GRANT CONNECT ON DATABASE databricks_postgres TO "<service-principal-id>";
GRANT USAGE ON SCHEMA public TO "<service-principal-id>";
GRANT SELECT ON TABLE your_table_name TO "<service-principal-id>";
            """,
            language="sql",
        )

    with col2:
        st.markdown(
            """
            **Databricks resources**
            * [Lakebase](https://docs.databricks.com/aws/en/oltp/) database instance (Postgres).
            * An existing Postgres database, schema, and table with data.
            """
        )

    with col3:
        st.markdown(
            """
            **Dependencies**
            * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk>=0.60.0`
            * [Psycopg](https://pypi.org/project/psycopg/) - `psycopg[binary]`
            * [Pandas](https://pypi.org/project/pandas/) - `pandas`
            * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
            """
        )

    st.info(
        "[This guide](https://docs.databricks.com/aws/en/oltp/query/sql-editor#create-a-new-query) "
        "shows you how to query your Lakebase."
    )

    st.warning(
        "⚠️ Tokens expire periodically; this app refreshes on each new connection and enforces TLS (sslmode=require)."
    )
