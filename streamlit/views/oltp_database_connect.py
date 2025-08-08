import uuid
import streamlit as st
import pandas as pd

from databricks.sdk import WorkspaceClient

import psycopg
from psycopg_pool import ConnectionPool


st.header("OLTP Database", divider=True)
st.subheader("Connect a table")
st.write(
    "This app connects to a [Databricks Lakebase](https://docs.databricks.com/aws/en/oltp/) OLTP database instance for reads and writes, e.g., of an App state. "
    "Provide the instance name, database, schema, and state table."
)


w = WorkspaceClient()

session_id = str(uuid.uuid4())
if "session_id" not in st.session_state:
    st.session_state["session_id"] = session_id


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
def build_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    conninfo = f"host={host} dbname={database} user={user}"
    return ConnectionPool(
        conninfo=conninfo,
        connection_class=RotatingTokenConnection,
        kwargs={"_instance_name": instance_name},
        min_size=1,
        max_size=10,
        open=True,
    )


def upsert_app_state(pool, session_id: str, state: dict):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            for key, value in state.items():
                cur.execute(f"""
                    INSERT INTO app_state (session_id, key, value, updated_at)
                    VALUES ('{session_id}', '{key}', '{value}', CURRENT_TIMESTAMP)
                    ON CONFLICT (session_id, key) DO UPDATE
                    SET value = EXCLUDED.value,
                        updated_at = CURRENT_TIMESTAMP
                """)
        conn.commit()


def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if not cur.description:
                return pd.DataFrame()
            
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()

    return pd.DataFrame(rows, columns=cols)


tab_try, tab_code, tab_reqs = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_try:
    instance_names = [i.name for i in w.database.list_database_instances()]
    instance_name = st.selectbox("Database instance:", instance_names)
    database = st.text_input("Database:", value="databricks_postgres")
    schema = st.text_input("Schema:", value="public")
    table = st.text_input("Table:", value="app_state")

    user = w.current_user.me().user_name
    host = ""
    if instance_name:
        host = w.database.get_database_instance(name=instance_name).read_write_dns

    if st.button("Run a query"):
        if not all([instance_name, host, database, table]):
            st.error("Please provide instance, database, and schema-table.")
        else:
            pool = build_pool(instance_name, host, user, database)

            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                session_id TEXT,
                key TEXT,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (session_id, key)
            )
            """
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(create_table_sql)
                conn.commit()

            state = {"feedback_message": "true"}
            upsert_app_state(pool, session_id, state)

            df = query_df(pool, f"SELECT * FROM {schema}.{table} WHERE session_id='{session_id}'")
            st.dataframe(df)

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

        
        class RotatingTokenConnection(psycopg.Connection):
            @classmethod
            def connect(cls, conninfo: str = "", **kwargs):
                kwargs["password"] = w.database.generate_database_credential(
                    request_id=str(uuid.uuid4()),
                    instance_names=[kwargs.pop("_instance_name")]
                ).token
                kwargs.setdefault("sslmode", "require")
                return super().connect(conninfo, **kwargs)

                
        @st.cache_resource
        def build_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
            return ConnectionPool(
                conninfo=f"host={host} dbname={database} user={user}",
                connection_class=RotatingTokenConnection,
                kwargs={"_instance_name": instance_name},
                min_size=1,
                max_size=5,
                open=True,
            )


        def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if cur.description is None:
                        return pd.DataFrame()
                    cols = [d.name for d in cur.description]
                    rows = cur.fetchall()
            return pd.DataFrame(rows, columns=cols)


        session_id = str(uuid.uuid4())
        if "session_id" not in st.session_state:
            st.session_state["session_id"] = session_id

            
        instance_name = "dbase_instance"
        database = "databricks_postgres"
        schema = "public"
        table = "app_state"
        user = w.current_user.me().user_name
        host = w.database.get_database_instance(name=instance_name).read_write_dns

        pool = build_pool(instance_name, host, user, database)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {schema}.{table} (
                    session_id TEXT,
                    key TEXT,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (session_id, key)
                )
                """)

                cur.execute(f"""
                    INSERT INTO app_state (session_id, key, value, updated_at)
                    VALUES ('{session_id}', 'feedback_message', 'true', CURRENT_TIMESTAMP)
                    ON CONFLICT (session_id, key) DO UPDATE
                    SET value = EXCLUDED.value,
                        updated_at = CURRENT_TIMESTAMP
                """)

        df = query_df(pool, f"SELECT * FROM {schema}.{table} WHERE session_id = '{session_id}'")
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
            * The database instance should be specified in your [**App resources**](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources).
            * A PostgreSQL role for the service principal is **required**.
            See [this guide](https://docs.databricks.com/aws/en/oltp/pg-roles?language=PostgreSQL#create-postgres-roles-and-grant-privileges-for-databricks-identities).
            * The PostgreSQL service principal role should have these example grants:
            """
        )
        st.code(
            '''
GRANT CONNECT ON DATABASE databricks_postgres TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
GRANT USAGE, CREATE ON SCHEMA public TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_state TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
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