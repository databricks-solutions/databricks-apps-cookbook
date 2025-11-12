import folium
import pandas as pd
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
from folium.plugins import Draw
from streamlit_folium import st_folium

import streamlit as st

st.header(body="Visualizations", divider=True)
st.subheader("Map display and interaction")
st.write(
    "This recipe enables you to display geographic data on a map and collect user geo input through interactive map drawing."
)

cfg = Config()

w = WorkspaceClient()

warehouses = w.warehouses.list()

warehouse_paths = {wh.name: wh.odbc_params.path for wh in warehouses}


@st.cache_resource
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


# Sample cities data
cities = [
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "Tokyo", "latitude": 35.6895, "longitude": 139.6917},
    {"name": "Sydney", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522},
    {"name": "Dubai", "latitude": 25.276987, "longitude": 55.296249},
    {"name": "Rio de Janeiro", "latitude": -22.9068, "longitude": -43.1729},
    {"name": "Moscow", "latitude": 55.7558, "longitude": 37.6173},
    {"name": "Cape Town", "latitude": -33.9249, "longitude": 18.4241},
]

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    # Sub-tabs for different functionalities
    subtab1, subtab2 = st.tabs(["Display geo data", "Draw on the map"])

    with subtab1:
        st.markdown("### Display data on a map")
        st.write(
            "Load a table from a Delta table and display the geographic data on a map."
        )

        display_option = st.radio(
            "Choose data source:",
            ["Sample data", "Load from a table"],
            horizontal=True,
        )

        if display_option == "Sample data":
            data = pd.DataFrame(cities)
            if st.button("Display sample data on map"):
                st.map(data, latitude="latitude", longitude="longitude")
                st.dataframe(data)
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

            if warehouse_selection and table_name:
                http_path = warehouse_paths[warehouse_selection]
                conn = get_connection(http_path)
                df = read_table(table_name, conn)

                st.dataframe(df)

                if "latitude" in df.columns and "longitude" in df.columns:
                    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
                    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
                    df = df.dropna(subset=["latitude", "longitude"])

                    if not df.empty:
                        st.map(df, latitude="latitude", longitude="longitude")
                else:
                    st.warning("No longitude, latitude found in the table")

    with subtab2:
        st.markdown("### Draw on the map")
        st.write("Enable users to pick geo points or draw geofences to be used.")

        choice = st.selectbox(
            "Select an input type",
            ["Points", "Geofences", "Polyline", "Rectangle", "Circle"],
        )

        st.write("Select points on the map below:")
        m = folium.Map(
            location=[37.7749, -122.4194], zoom_start=13
        )  # Example: San Francisco
        draw = Draw(
            draw_options={
                "polyline": True if choice == "Polyline" else False,
                "rectangle": True if choice == "Rectangle" else False,
                "circle": True if choice == "Circle" else False,
                "marker": True if choice == "Points" else False,
                "circlemarker": False,
                "polygon": True if choice == "Geofences" else False,
            },
            edit_options={"edit": True},
        )
        draw.add_to(m)
        output = st_folium(m, width=700, height=500)

        with st.expander(
            "Click to see the last active selected map input", expanded=False
        ):
            if (
                output["last_active_drawing"]
                and "geometry" in output["last_active_drawing"]
            ):
                st.json(output["last_active_drawing"]["geometry"])

with tab_b:
    st.markdown("### Display geo data from a table")
    st.code(
        """
import streamlit as st
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
st.map(df, latitude="latitude", longitude="longitude")
    """
    )

    st.markdown("### Collect user geo input")
    st.code(
        """
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

# Create a map centered on a location
m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)

# Enable drawing tools (set True for the tools you want to enable)
draw = Draw(
    draw_options={
        "marker": True,      # For collecting points
        "polygon": True,     # For collecting geofences/polygons
        "polyline": True,    # For collecting polylines
        "rectangle": True,   # For collecting rectangles
        "circle": True,      # For collecting circles
        "circlemarker": False,
    },
    edit_options={"edit": True},
)
draw.add_to(m)
output = st_folium(m, width=700, height=500)

# Access the drawn geometry
if output["last_active_drawing"] and "geometry" in output["last_active_drawing"]:
    geometry = output["last_active_drawing"]["geometry"]
    st.json(geometry)
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
                    * [Streamlit Folium](https://pypi.org/project/streamlit-folium/) - `streamlit-folium`
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk` _(for table data)_
                    * [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector` _(for table data)_
                    """
        )
