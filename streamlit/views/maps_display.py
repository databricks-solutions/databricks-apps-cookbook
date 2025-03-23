
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd


st.header("Geo Visualization", divider=True)
st.subheader("Read a table and display as a map")
st.write("This receipt loads a table from a delta table and displays the data on a map.")

cfg = Config()

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
    {"name": "Cape Town", "latitude": -33.9249, "longitude": 18.4241}
]

data = pd.DataFrame(cities)


tab_a, tab_b, tab_c, tab_d = st.tabs(["**Try it**","**Try it with a delta table**", "**Code snippet**", "**Requirements**"])

with tab_a:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try It with a random sample"):
            st.map(data, latitude="Latitude", longitude="Longitude")
            st.dataframe(data)


with tab_b:
    col1, col2 = st.columns(2)
    with col1:
        http_path_input = st.text_input(
            "Enter your Databricks HTTP Path:", placeholder="/sql/1.0/warehouses/xxxxxx"
        )

        table_name = st.text_input(
            "Specify a Unity Catalog table name:", placeholder="catalog.schema.table"
        )
        st.info("For displaying a sample, please use the table samples.accuweather.forecast_daily_calendar_metric")

        if http_path_input and table_name:
            conn = get_connection(http_path_input)
            df = read_table(table_name, conn)
            
            st.dataframe(df)

            if 'latitude' in df.columns and 'longitude' in df.columns:
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                df = df.dropna(subset=['latitude', 'longitude'])
                
                if not df.empty:
                    st.map(df, latitude="latitude", longitude="longitude")
            else:
                st.warning("no longitude, latitude found in the table")


table = [
    {
        "type": "Get Tables",
        "param": "Get long lat from the tables",
        "description": "Get long lat from the tables.",
        "code": """
        ```python
        def read_table(table_name, conn):
            with conn.cursor() as cursor:
                query = f"SELECT * FROM {table_name} LIMIT 1000"
                cursor.execute(query)
                return cursor.fetchall_arrow().to_pandas()
        ```
        """,
    },
    {
        "type": "Display Maps",
        "param": "Display pandas df as maü",
        "description": "Display the streamlit map",
        "code": """
        ```python
            conn = get_connection(http_path_input)
            df = read_table(table_name, conn)
            
            st.dataframe(df)

            if 'latitude' in df.columns and 'longitude' in df.columns:
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                df = df.dropna(subset=['latitude', 'longitude'])
                
                if not df.empty:
                    st.map(df, latitude="latitude", longitude="longitude")
            else:
                st.warning("no longitude, latitude found in the table")


        ```
        """,
    },
]

with tab_c:
    for i, row in enumerate(table):
        with st.expander(f"**{row['type']} ({row['param']})**", expanded=(i == 0)):
            st.markdown(f"**Description**: {row['description']}")
            st.markdown(row["code"])
