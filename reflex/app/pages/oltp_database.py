import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.components.loading_spinner import loading_spinner
from app.states.oltp_database_state import OltpDatabaseState
from app import theme

CODE_SNIPPET = '''
import uuid
import reflex as rx
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


_pool = None

def get_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=f"host={host} dbname={database} user={user}",
            connection_class=RotatingTokenConnection,
            kwargs={"_instance_name": instance_name},
            min_size=1,
            max_size=5,
            open=True,
        )
    return _pool


def query_df(pool: ConnectionPool, sql: str) -> pd.DataFrame:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description is None:
                return pd.DataFrame()
            cols = [d.name for d in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


class OltpDatabaseState(rx.State):
    session_id: str = ""
    instance_name: str = "dbase_instance"
    database: str = "databricks_postgres"
    schema: str = "public"
    table: str = "app_state"
    df_data: list[list] = []
    df_columns: list[dict] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.session_id = str(uuid.uuid4())

        try:
            user = w.current_user.me().user_name
            host = w.database.get_database_instance(name=self.instance_name).read_write_dns
            pool = get_pool(self.instance_name, host, user, self.database)

            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.{self.table} (
                        session_id TEXT,
                        key TEXT,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (session_id, key)
                    )
                    """)

                    cur.execute(f"""
                        INSERT INTO {self.schema}.{self.table} (session_id, key, value, updated_at)
                        VALUES ('{self.session_id}', 'feedback_message', 'true', CURRENT_TIMESTAMP)
                        ON CONFLICT (session_id, key) DO UPDATE
                        SET value = EXCLUDED.value,
                            updated_at = CURRENT_TIMESTAMP
                    """)

            df = query_df(pool, f"SELECT * FROM {self.schema}.{self.table} WHERE session_id = '{self.session_id}'")
            data = df.values.tolist()
            columns = [{"title": col, "id": col, "type": "str"} for col in df.columns]

            async with self:
                self.df_data = data
                self.df_columns = columns
        except Exception as e:
            async with self:
                self.error_message = str(e)
        finally:
            async with self:
                self.is_loading = False
'''


def oltp_db_requirements() -> rx.Component:
    sql_code = """-- The service principal needs to be granted `CONNECT` on the database,
-- `USAGE` and `CREATE` on the schema, and `SELECT`, `INSERT`, `UPDATE`, `DELETE`
-- on the table.

GRANT CONNECT ON DATABASE databricks_postgres TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
GRANT USAGE, CREATE ON SCHEMA public TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE app_state TO "099f0306-9e29-4a87-84c0-3046e4bcea02";
"""
    return rx.vstack(
        rx.grid(
            rx.vstack(
                rx.heading(
                    "Permissions (app service principal)",
                    size="4",
                    class_name="font-semibold text-gray-800",
                ),
                rx.markdown(
                    "The service principal used for this app's authentication requires privileges to access the target database. You can read more about [App resources](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources) and the [PostgreSQL roles guide](https://docs.databricks.com/aws/en/oltp/pg-roles?language=PostgreSQL#create-postgres-roles-and-grant-privileges-for-databricks-identities).",
                    class_name="text-sm text-gray-600",
                ),
                rx.code_block(sql_code, language="sql", class_name="mt-2 text-sm"),
                rx.markdown(
                    "For more information on querying from Lakebase, check out the [Lakebase query guide](https://learn.microsoft.com/en-us/azure/databricks/oltp/query/sql-editor#create-a-new-query).",
                    class_name="text-sm text-gray-600 mt-2",
                ),
                class_name="p-4 bg-gray-50 rounded-lg h-full",
                align="start",
            ),
            rx.vstack(
                rx.heading(
                    "Databricks resources",
                    size="4",
                    class_name="font-semibold text-gray-800",
                ),
                rx.el.ul(
                    rx.el.li("An installed Lakebase Postgres instance."),
                    rx.el.li("The target PostgreSQL database name."),
                    rx.el.li("The target PostgreSQL schema name."),
                    rx.el.li("The target PostgreSQL table name."),
                    class_name="list-disc list-inside text-sm text-gray-600 pl-2",
                ),
                rx.markdown(
                    "For more information, check out the [Lakebase documentation](https://docs.databricks.com/aws/en/oltp/).",
                    class_name="text-sm text-gray-600 mt-2",
                ),
                class_name="p-4 bg-gray-50 rounded-lg h-full",
                align="start",
            ),
            rx.vstack(
                rx.heading(
                    "Dependencies", size="4", class_name="font-semibold text-gray-800"
                ),
                rx.el.ul(
                    rx.el.li("psycopg[binary]"),
                    rx.el.li("psycopg_pool"),
                    rx.el.li("databricks-sdk"),
                    rx.el.li("reflex"),
                    rx.el.li("pandas"),
                    class_name="list-disc list-inside text-sm text-gray-600 pl-2",
                ),
                class_name="p-4 bg-gray-50 rounded-lg h-full",
                align="start",
            ),
            columns="3",
            spacing="4",
            width="100%",
        ),
        rx.markdown(
            "**Note**: The OAuth token used for the connection is valid for 60 minutes. This example uses a connection pool that automatically refreshes the token for each new connection. It also requires TLS for all connections.",
            class_name="text-sm text-gray-500 mt-4 italic",
        ),
        align="start",
        width="100%",
    )


def oltp_db_content() -> rx.Component:
    """Content for the 'Try It' tab of the OLTP DB page."""
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Instance Name", class_name="font-semibold text-sm"),
                rx.el.input(
                    default_value=OltpDatabaseState.instance_name,
                    on_change=OltpDatabaseState.set_instance_name,
                    class_name="w-full p-2 border rounded-md",
                ),
                align="start",
                width="100%",
            ),
            rx.vstack(
                rx.text("Database", class_name="font-semibold text-sm"),
                rx.el.input(
                    default_value=OltpDatabaseState.database,
                    on_change=OltpDatabaseState.set_database,
                    class_name="w-full p-2 border rounded-md",
                ),
                align="start",
                width="100%",
            ),
            rx.vstack(
                rx.text("Schema", class_name="font-semibold text-sm"),
                rx.el.input(
                    default_value=OltpDatabaseState.schema_name,
                    on_change=OltpDatabaseState.set_schema_name,
                    class_name="w-full p-2 border rounded-md",
                ),
                align="start",
                width="100%",
            ),
            rx.vstack(
                rx.text("Table", class_name="font-semibold text-sm"),
                rx.el.input(
                    default_value=OltpDatabaseState.table,
                    on_change=OltpDatabaseState.set_table,
                    class_name="w-full p-2 border rounded-md",
                ),
                align="start",
                width="100%",
            ),
            spacing="4",
            class_name="w-full mb-4",
        ),
        rx.button(
            "Run a query",
            on_click=OltpDatabaseState.run_query,
            is_loading=OltpDatabaseState.is_loading,
            bg=theme.PRIMARY_COLOR,
            color="white",
            _hover={"opacity": 0.8},
        ),
        rx.cond(
            OltpDatabaseState.error_message,
            rx.box(
                rx.icon(tag="flag_triangle_right", class_name="text-red-500 mr-2"),
                rx.text(OltpDatabaseState.error_message, color="red.500"),
                class_name="flex items-center p-4 mt-4 bg-red-50 border border-red-200 rounded-lg",
            ),
            None,
        ),
        rx.cond(
            OltpDatabaseState.is_loading,
            loading_spinner("Connecting to database and running query..."),
            rx.cond(
                OltpDatabaseState.df_data,
                rx.data_editor(
                    data=OltpDatabaseState.df_data,
                    columns=OltpDatabaseState.df_columns,
                    height="60vh",
                    width="95%",
                    class_name="mt-4 overflow-auto",
                    is_readonly=True,
                ),
                rx.box(
                    rx.text(
                        "Query executed successfully, but returned no data. The table is ready.",
                        class_name="text-gray-600",
                    ),
                    class_name="p-4 bg-gray-50 rounded-lg mt-4 w-full text-center",
                ),
            ),
        ),
        align="start",
        width="100%",
        spacing="4",
    )


def oltp_database_page() -> rx.Component:
    """The OLTP Database sample page."""
    return main_layout(
        tabbed_page_template(
            page_title="OLTP Database Integration",
            page_description="Connect to and interact with a transactional database (e.g., PostgreSQL) directly from your Reflex app using rotating OAuth tokens.",
            try_it_content=oltp_db_content,
            code_snippet_content=CODE_SNIPPET,
            requirements_content=oltp_db_requirements,
        )
    )