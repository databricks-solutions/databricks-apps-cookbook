import uuid
import streamlit as st
import pandas as pd

from databricks.sdk import WorkspaceClient

import psycopg
from psycopg_pool import ConnectionPool


st.header("OLTP Database", divider=True)
st.subheader("Connect a table")
st.write(
    "This app connects to a [Databricks Lakebase](https://docs.databricks.com/aws/en/oltp/) OLTP database instance. "
    "Provide the instance name, database, schema, and table."
)


w = WorkspaceClient()


def generate_token(instance_name: str) -> str:
    cred = w.database.generate_database_credential(
        request_id=str(uuid.uuid4()), instance_names=[instance_name]
    )
    return cred.token


class RotatingTokenConnection(psycopg.Connection):
    """psycopg3 Connection that injects a fresh OAuth token as the password."""

    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        instance_name = kwargs.pop("_instance_name")
        kwargs["password"] = generate_token(instance_name)
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)


@st.cache_resource
def build_pool(*, instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    conninfo = f"host={host} dbname={database} user={user}"
    return ConnectionPool(
        conninfo=conninfo,
        connection_class=RotatingTokenConnection,
        kwargs={"_instance_name": instance_name},
        min_size=1,
        max_size=10,
        open=True,
    )


def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


tab_try, tab_code, tab_reqs = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_try:
    instance_names = [i.name for i in w.database.list_database_instances()]
    instance_name = st.selectbox("Database instance:", instance_names)
    database = st.text_input("Database:", placeholder="customer_database")
    table = st.text_input("Table in a database schema:", placeholder="customer_core.customers_oltp")
    limit = st.text_input("Limit:", value=10)

    user = w.current_user.me().user_name
    host = ""
    if instance_name:
        host = w.database.get_database_instance(name=instance_name).read_write_dns

    if st.button("Run a query"):
        if not all([instance_name, host, database, table]):
            st.error("Please provide instance, database, and schema-table.")
        else:
            pool = build_pool(instance_name=instance_name, host=host, user=user, database=database)
            sql = f"SELECT * FROM {table} LIMIT {int(limit)};"
            df = query_df(pool, sql)
            st.dataframe(df, use_container_width=True)

with tab_code:
    st.code(
        '''
import uuid
import streamlit as st
import pandas as pd

from databricks.sdk import WorkspaceClient

import psycopg
from psycopg_pool import ConnectionPool


w = WorkspaceClient()


def generate_token(instance_name: str) -> str:
    cred = w.database.generate_database_credential(
        request_id=str(uuid.uuid4()), instance_names=[instance_name]
    )

    return cred.token

    
class RotatingTokenConnection(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        instance_name = kwargs.pop("_instance_name")
        kwargs["password"] = generate_token(instance_name)
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)

        
@st.cache_resource
def build_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    return ConnectionPool(
        conninfo=f"host={host} dbname={database} user={user}",
        connection_class=RotatingTokenConnection,
        kwargs={"_instance_name": instance_name},
        min_size=1,
        max_size=10,
        open=True,
    )

    
def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=cols)

    
instance_name = "dbase_instance"
database = "customer_database"
table = "customer_core.customers_oltp"
user = w.current_user.me().user_name
host = w.database.get_database_instance(name=instance_name).read_write_dns

pool = build_pool(instance_name, host, user, database)
df = query_df(pool, f'SELECT * FROM {table} LIMIT 100')
st.dataframe(df)
        ''',
        language="python",
    )

with tab_reqs:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            **Permissions (app service principal)**
            * A PostgreSQL role for the service principal is **required**.
            See [this guide](https://docs.databricks.com/aws/en/oltp/pg-roles?language=PostgreSQL#create-postgres-roles-and-grant-privileges-for-databricks-identities).
            * The PostgreSQL service principal role should have these example grants:
            """
        )
        st.code(
            '''
GRANT CONNECT ON DATABASE customer_database TO "<YOUR-SERVICE-PRINCIPAL-ID>";
GRANT USAGE ON SCHEMA customer_core TO "<YOUR-SERVICE-PRINCIPAL-ID>";
GRANT SELECT ON TABLE customers_oltp TO "<YOUR-SERVICE-PRINCIPAL-ID>";
            ''',
            language="sql",
        )
        st.caption(
            "[This guide](https://learn.microsoft.com/en-us/azure/databricks/oltp/query/sql-editor#create-a-new-query) "
            "shows you how to query your Lakebase."
        )

    with col2:
        st.markdown(
            """
            **Databricks resources**
            * [Lakebase](https://docs.databricks.com/aws/en/oltp/) database instance (PostgreSQL).
            * Target PostgreSQL database/schema/table.
            """
        )

    with col3:
        st.markdown(
            """
            **Dependencies**
            * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
            * [`psycopg[binary]`](https://pypi.org/project/psycopg/), [`psycopg-pool`](https://pypi.org/project/psycopg-pool/)
            * [Pandas](https://pypi.org/project/pandas/) - `pandas`
            * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
            """
        )

    st.caption(
        "Tokens expire periodically; this app refreshes on each new connection and enforces TLS (sslmode=require)."
    )