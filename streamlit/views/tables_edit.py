import pandas as pd
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

import streamlit as st

st.header(body="Tables", divider=True)
st.subheader("Edit a Delta table")
st.write(
    "Use this recipe to read, edit, and write back data stored in a small Unity Catalog table "
    "with [Databricks SQL Connector]"
    "(https://docs.databricks.com/en/dev-tools/python-sql-connector.html)."
)

cfg = Config()

w = WorkspaceClient()

warehouses = w.warehouses.list()

warehouse_paths = {wh.name: wh.odbc_params.path for wh in warehouses}

catalogs = w.catalogs.list()


@st.cache_resource(ttl="1h")
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()


def get_schema_names(catalog_name):
    schemas = w.schemas.list(catalog_name=catalog_name)
    return [schema.name for schema in schemas]


def get_table_names(catalog_name, schema_name):
    tables = w.tables.list(catalog_name=catalog_name, schema_name=schema_name)
    return [table.name for table in tables]


def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
    progress = st.empty()
    with conn.cursor() as cursor:
        rows = list(df.itertuples(index=False))
        values = ",".join([f"({','.join(map(repr, row))})" for row in rows])
        with progress:
            st.info("Calling Databricks SQL...")
        cursor.execute(f"INSERT OVERWRITE {table_name} VALUES {values}")
    progress.empty()
    st.success("Changes saved")


tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    http_path_input = st.selectbox(
        "Select a SQL warehouse:", [""] + list(warehouse_paths.keys())
    )

    catalog_name = st.selectbox(
        "Select a catalog:", [""] + [catalog.name for catalog in catalogs]
    )

    if catalog_name and catalog_name != "":
        schema_names = get_schema_names(catalog_name)
        schema_name = st.selectbox("Select a schema:", [""] + schema_names)

    if catalog_name and catalog_name != "" and schema_name and schema_name != "":
        table_names = get_table_names(catalog_name, schema_name)
        table_name = st.selectbox("Select a table:", [""] + table_names)

        in_table_name = f"{catalog_name}.{schema_name}.{table_name}"

        if (
            http_path_input
            and table_name
            and catalog_name
            and schema_name
            and table_name != ""
        ):
            http_path = warehouse_paths[http_path_input]
            conn = get_connection(http_path)
            original_df = read_table(in_table_name, conn)
            edited_df = st.data_editor(original_df, num_rows="dynamic", hide_index=True)

            df_diff = pd.concat([original_df, edited_df]).drop_duplicates(keep=False)
            if not df_diff.empty:
                if st.button("Save changes"):
                    insert_overwrite_table(in_table_name, edited_df, conn)


with tab_b:
    st.code(
        """
        import pandas as pd
        import streamlit as st
        from databricks import sql
        from databricks.sdk.core import Config


        cfg = Config() # Set the DATABRICKS_HOST environment variable when running locally


        @st.cache_resource(ttl="1h")
        def get_connection(http_path):
            return sql.connect(
                server_hostname=cfg.host,
                http_path=http_path,
                credentials_provider=lambda: cfg.authenticate,
            )


        def read_table(table_name: str, conn) -> pd.DataFrame:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name}")
                return cursor.fetchall_arrow().to_pandas()


        def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
            progress = st.empty()
            with conn.cursor() as cursor:
                rows = list(df.itertuples(index=False))
                values = ",".join([f"({','.join(map(repr, row))})" for row in rows])
                with progress:
                    st.info("Calling Databricks SQL...")
                cursor.execute(f"INSERT OVERWRITE {table_name} VALUES {values}")
            progress.empty()
            st.success("Changes saved")


        http_path_input = st.text_input(
            "Specify the HTTP Path to your Databricks SQL Warehouse:",
            placeholder="/sql/1.0/warehouses/xxxxxx",
        )

        table_name = st.text_input(
            "Specify a Catalog table name:", placeholder="catalog.schema.table"
        )

        if http_path_input and table_name:
            conn = get_connection(http_path_input)
            original_df = read_table(table_name, conn)
            edited_df = st.data_editor(original_df, num_rows="dynamic", hide_index=True)

            df_diff = pd.concat([original_df, edited_df]).drop_duplicates(keep=False)
            if not df_diff.empty:
                if st.button("Save changes"):
                    insert_overwrite_table(table_name, edited_df, conn)
        else:
            st.warning("Provide both the warehouse path and a table name to load data.")
        """
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            **Permissions (app service principal)**
            * `MODIFY` on the Unity Catalog table
            * `CAN USE` on the SQL warehouse
            """
        )
    with col2:
        st.markdown(
            """
            **Databricks resources**
            * SQL warehouse
            * Unity Catalog table
            """
        )
    with col3:
        st.markdown(
            """
            **Dependencies**
            * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
            * [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector`
            * [Pandas](https://pypi.org/project/pandas/) - `pandas`
            * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
            """
        )
