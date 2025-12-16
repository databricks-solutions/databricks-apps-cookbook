import reflex as rx
from app.components.page_layout import main_layout
from app.components.tabbed_page_template import tabbed_page_template
from app.states.oltp_database_state import OltpDatabaseState
from app import theme

CODE_SNIPPET = '''
import reflex as rx
import uuid
import pandas as pd
from databricks.sdk import WorkspaceClient
import psycopg
from psycopg_pool import ConnectionPool
from typing import Union, Optional
import datetime

# This module-level variable will cache the connection pool across the app.
_pool: Optional[ConnectionPool] = None

# Define a custom connection class to handle token rotation.
class RotatingTokenConnection(psycopg.Connection):
    def __init__(self, *args, **kwargs):
        self._instance_name = kwargs.pop("_instance_name")
        super().__init__(*args, **kwargs)

    @classmethod
    def connect(cls, *args, **kwargs):
        if "_instance_name" in kwargs:
            instance_name = kwargs["_instance_name"]
            # Generate a fresh OAuth token for each new connection.
            w = WorkspaceClient()
            credential = w.database.generate_database_credential(
                request_id=str(uuid.uuid4()), instance_names=[instance_name]
            )
            kwargs["password"] = credential.token
        return super().connect(*args, **kwargs)


def build_pool(instance_name: str, host: str, user: str, database: str) -> ConnectionPool:
    """Builds and returns a new connection pool with token rotation."""
    # Note: sslmode is set to require to ensure encrypted connections.
    return ConnectionPool(
        conninfo=f"host={host} dbname={database} user={user} sslmode=require",
        min_size=1,
        max_size=5,
        open=True,
        kwargs={"_instance_name": instance_name},
        connection_class=RotatingTokenConnection,
    )

def query_df(query: str, params=None) -> pd.DataFrame:
    """Executes a query using the global pool and returns a DataFrame."""
    global _pool
    if _pool is None:
        raise ConnectionError("Connection pool is not initialized.")
    with _pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description is None:
                return pd.DataFrame()
            cols = [desc[0] for desc in cursor.description]
            return pd.DataFrame(cursor.fetchall(), columns=cols)


def upsert_app_state(schema: str, table: str, session_id: str, key: str, value: str):
    """Helper to create a table and upsert a key-value pair for a session."""
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{table} (
        session_id TEXT,
        key TEXT,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (session_id, key)
    );
    """
    query_df(create_sql)

    upsert_sql = f"""
    INSERT INTO {schema}.{table} (session_id, key, value, updated_at) 
    VALUES (%(session_id)s, %(key)s, %(value)s, CURRENT_TIMESTAMP)
    ON CONFLICT (session_id, key) DO UPDATE SET
        value = EXCLUDED.value,
        updated_at = EXCLUDED.updated_at;
    """
    query_df(upsert_sql, params={"session_id": session_id, "key": key, "value": value})


class OltpDatabaseState(rx.State):
    session_id: str = str(uuid.uuid4())
    selected_instance: str = "your_instance_name"
    database: str = "databricks_postgres"
    schema_name: str = "public"
    table_name: str = "app_state"
    result_data: list[dict[str, Union[str, int, float, bool, None, datetime.datetime]]] = []
    is_loading: bool = False
    error_message: str = ""

    @rx.event(background=True)
    async def run_query(self):
        global _pool
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            # Initialize the pool if it's the first run.
            if _pool is None:
                w = WorkspaceClient()
                user = w.current_user.me().user_name
                instance = w.database.get_database_instance(name=self.selected_instance)
                host = instance.read_write_dns
                _pool = build_pool(
                    instance_name=self.selected_instance,
                    host=host, user=user, database=self.database
                )

            # Create table and insert/update a record for this session.
            upsert_app_state(
                self.schema_name, self.table_name, self.session_id, "feedback_message", "true"
            )

            # Fetch the data to display.
            select_sql = f"SELECT * FROM {self.schema_name}.{self.table_name} WHERE session_id = %(session_id)s"
            df = query_df(select_sql, params={"session_id": self.session_id})

            async with self:
                self.result_data = df.to_dict("records")

        except Exception as e:
            async with self:
                self.error_message = f"An error occurred: {e}"
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
                    rx.el.li(
                        rx.link(
                            "reflex",
                            href="https://pypi.org/project/reflex/",
                            is_external=True,
                        )
                    ),
                    rx.el.li("databricks-sdk>=0.60.0"),
                    rx.el.li("psycopg[binary]"),
                    rx.el.li("psycopg-pool"),
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
                rx.select(
                    OltpDatabaseState.instance_names,
                    placeholder="Select an instance...",
                    on_change=OltpDatabaseState.set_selected_instance,
                    value=OltpDatabaseState.selected_instance,
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
                    default_value=OltpDatabaseState.table_name,
                    on_change=OltpDatabaseState.set_table_name,
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
            rx.vstack(
                rx.spinner(size="3"),
                rx.text("Connecting to database and running query..."),
                align="center",
                justify="center",
                class_name="w-full h-48 bg-gray-50 rounded-lg mt-4",
            ),
            rx.cond(
                OltpDatabaseState.result_data,
                rx.data_editor(
                    data=OltpDatabaseState.result_data_for_editor,
                    columns=OltpDatabaseState.result_columns_for_editor,
                    class_name="mt-4 w-full",
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