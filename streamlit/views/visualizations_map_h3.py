import pandas as pd
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import streamlit_hexviz as shv
import streamlit as st
import numpy as np

st.header(body="Visualizations", divider=True)
st.subheader("Map display with geo spatial index H3")
st.write(
    "This recipe enables you to display geographic data on a map with H3"
)

cfg = Config()

w = WorkspaceClient()

warehouses = w.warehouses.list()

warehouse_paths = {wh.name: wh.odbc_params.path for wh in warehouses}


@st.cache_resource(ttl=300, show_spinner=True)
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


def make_london(n: int) -> pd.DataFrame:
    """Simulate London bike hire density."""
    rng = np.random.default_rng(7)
    lats = rng.normal(51.505, 0.04, n)
    lons = rng.normal(-0.12, 0.05, n)
    duration = rng.exponential(1200, n)
    return pd.DataFrame({"lat": lats, "lon": lons, "duration_s": duration})


tab_a, tab_b, tab_c = st.tabs(
    ["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    # Sub-tabs for different functionalities
    st.markdown("### Display data on a map")
    st.write(
        "Load a table from a Delta table and display the geographic data on a map."
    )

    display_option = st.radio(
        "Choose data source:",
        ["Sample data", "Load from a table", "Load from a table with H3 index"],
        horizontal=True,
    )

    if display_option == "Sample data":
        data = make_london(2000)
        shv.h3_map(data, lat="lat", lon="lon")
    else:
        warehouse_selection = st.selectbox(
            "Select a SQL Warehouse:",
            options=[""] + list(warehouse_paths.keys()),
            help="Warehouse list populated from your workspace using app service principal.",
        )

        table_name = st.text_input(
            "Specify a Unity Catalog table name:",
            value="samples.accuweather.forecast_daily_calendar_metric",
            help="Use this example table or input your own",
        )

        if display_option == "Load from a table":
            if warehouse_selection and table_name:
                http_path = warehouse_paths[warehouse_selection]
                conn = get_connection(http_path)
                df = read_table(table_name, conn)

                st.dataframe(df)

                if "latitude" in df.columns and "longitude" in df.columns:
                    df["latitude"] = pd.to_numeric(
                        df["latitude"], errors="coerce")
                    df["longitude"] = pd.to_numeric(
                        df["longitude"], errors="coerce")
                    df = df.dropna(subset=["latitude", "longitude"])

                    if not df.empty:
                        shv.h3_map(df, lat="latitude", lon="longitude")
                else:
                    st.warning("No longitude, latitude found in the table")
        else:
            h3_col = st.text_input('Specify H3 index')
            if h3_col:
                if warehouse_selection and table_name:
                    http_path = warehouse_paths[warehouse_selection]
                    conn = get_connection(http_path)
                    df = read_table(table_name, conn)

                    st.dataframe(df)

                    try:
                        shv.h3_choropleth(df, h3_col=h3_col)
                    except:
                        st.warning('no H3 index found')
    st.info('Streamlit-hexviz enables users to navigate through the different resolutions and change coloring with navigation in the sidebar')
with tab_b:
    st.markdown("### Display geo data from a table")
    st.code(
        """
import streamlit as st
import streamlit_hexviz as shv
from databricks import sql
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
import pandas as pd

cfg = Config()
w = WorkspaceClient()

# List available SQL warehouses
warehouses = w.warehouses.list()
warehouse_paths = {wh.name: wh.odbc_params.path for wh in warehouses}

# Connect to SQL warehouse
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

# Read table
def read_table(table_name, conn):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

# Get data and display on map
warehouse_name = "your_warehouse_name"
table_name = "samples.accuweather.forecast_daily_calendar_metric"

http_path = warehouse_paths[warehouse_name]
conn = get_connection(http_path)
df = read_table(table_name, conn)

# Display map with latitude/longitude columns
shv.h3_map(df, lat="latitude", lon="longitude")


# Display map in case table contains H3 index
h3_col= 'your_h3_column_name'
shv.h3_choropleth(df, h3_col=h3_col)

    """
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
                    **Permissions (app service principal)**
                    * `CAN USE` on the SQL warehouse
                    * `SELECT` on the Unity Catalog table
                    
                    _Note: Only required if reading data from tables_
                    """
        )
    with col2:
        st.markdown(
            """
                    **Databricks resources**
                    * SQL warehouse _(optional, only for reading table data)_
                    * Unity Catalog table _(optional, only for reading table data)_
                    """
        )
    with col3:
        st.markdown(
            """
                    **Dependencies**
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    * [Streamlit Hexviz](https://pypi.org/project/streamlit-hexviz/) - `streamlit-hexviz`
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk` _(for table data)_
                    * [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector` _(for table data)_
                    """
        )
