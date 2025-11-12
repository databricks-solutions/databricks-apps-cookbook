import pandas as pd
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

import streamlit as st

st.header(body="Visualizations", divider=True)
st.subheader("Charts")
st.write(
    "This recipe demonstrates how to visualize data using Streamlit's built-in chart components: area charts, line charts, and bar charts."
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
        query = f"SELECT * FROM {table_name} LIMIT 1000"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()


tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    st.markdown("### Load data and visualize with charts")
    st.write(
        "Select a warehouse and load data from a Unity Catalog table to visualize with different chart types."
    )

    warehouse_selection = st.selectbox(
        "Select a SQL Warehouse:",
        options=[""] + list(warehouse_paths.keys()),
        help="Warehouse list populated from your workspace using app service principal.",
    )

    st.markdown("**Table:** `samples.nyctaxi.trips`")
    table_name = "samples.nyctaxi.trips"

    if st.button("Load Data", type="primary"):
        if not warehouse_selection:
            st.warning("Please select a SQL warehouse")
        else:
            with st.spinner("Loading data..."):
                try:
                    http_path = warehouse_paths[warehouse_selection]
                    conn = get_connection(http_path)
                    df = read_table(table_name, conn)

                    if df.empty:
                        st.warning("The query returned no data")
                    else:
                        st.success(f"Loaded {len(df)} rows from {table_name}")

                        # Store data in session state for chart display
                        st.session_state.chart_data = df

                except Exception as e:
                    st.error(f"Error loading data: {str(e)}")

    # Display charts if data is loaded
    if "chart_data" in st.session_state:
        df = st.session_state.chart_data

        # Process data for business insights
        try:
            df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
            df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
            df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
            df["pickup_day"] = df["tpep_pickup_datetime"].dt.day_name()
            df["trip_duration_minutes"] = (
                df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
            ).dt.total_seconds() / 60
        except Exception as e:
            st.error(f"Error processing datetime columns: {str(e)}")

        st.divider()
        st.markdown("### Data Preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.divider()

        # Create sub-tabs for different business insights
        chart_tab1, chart_tab2, chart_tab3, chart_tab4, chart_tab5 = st.tabs(
            [
                "Demand Patterns",
                "Revenue Analysis",
                "Trip Characteristics",
                "Popular Locations",
                "Time Analysis",
            ]
        )

        with chart_tab1:
            st.markdown("#### Demand by Hour of Day")
            st.write("Understand peak demand hours to optimize fleet deployment")

            if "pickup_hour" in df.columns:
                # Count trips by hour
                hourly_demand = df["pickup_hour"].value_counts().sort_index()
                st.bar_chart(hourly_demand, use_container_width=True)

                peak_hour = hourly_demand.idxmax()
                st.info(
                    f"🚕 Peak demand hour: {peak_hour}:00 with {hourly_demand.max()} trips"
                )
            else:
                st.warning("Required columns not found in the data")

        with chart_tab2:
            st.markdown("#### Revenue Patterns")
            st.write("Track revenue trends and identify high-earning periods")

            col1, col2 = st.columns(2)

            with col1:
                if "pickup_hour" in df.columns and "fare_amount" in df.columns:
                    st.markdown("**Average Fare by Hour**")
                    avg_fare_by_hour = df.groupby("pickup_hour")["fare_amount"].mean()
                    st.line_chart(avg_fare_by_hour, use_container_width=True)

                    best_hour = avg_fare_by_hour.idxmax()
                    st.success(
                        f"💰 Best earning hour: {best_hour}:00 (${avg_fare_by_hour.max():.2f} avg)"
                    )

            with col2:
                if "tpep_pickup_datetime" in df.columns and "fare_amount" in df.columns:
                    st.markdown("**Total Revenue Over Time**")
                    revenue_df = df.set_index("tpep_pickup_datetime")[
                        ["fare_amount"]
                    ].sort_index()
                    revenue_df["cumulative_revenue"] = revenue_df[
                        "fare_amount"
                    ].cumsum()
                    st.area_chart(
                        revenue_df["cumulative_revenue"], use_container_width=True
                    )

        with chart_tab3:
            st.markdown("#### Trip Characteristics")
            st.write("Analyze typical trip patterns to improve service")

            col1, col2 = st.columns(2)

            with col1:
                if "trip_distance" in df.columns:
                    st.markdown("**Trip Distance Distribution**")
                    # Create histogram-style data
                    distance_bins = pd.cut(df["trip_distance"], bins=20)
                    distance_counts = distance_bins.value_counts().sort_index()
                    # Convert interval index to strings for charting
                    distance_counts.index = distance_counts.index.astype(str)
                    st.bar_chart(distance_counts, use_container_width=True)

                    avg_distance = df["trip_distance"].mean()
                    st.info(f"📏 Average trip distance: {avg_distance:.2f} miles")

            with col2:
                if "trip_duration_minutes" in df.columns:
                    st.markdown("**Trip Duration Distribution**")
                    # Filter out outliers (trips > 120 minutes)
                    duration_df = df[df["trip_duration_minutes"] <= 120]
                    duration_bins = pd.cut(
                        duration_df["trip_duration_minutes"], bins=20
                    )
                    duration_counts = duration_bins.value_counts().sort_index()
                    # Convert interval index to strings for charting
                    duration_counts.index = duration_counts.index.astype(str)
                    st.bar_chart(duration_counts, use_container_width=True)

                    avg_duration = df["trip_duration_minutes"].mean()
                    st.info(f"⏱️ Average trip duration: {avg_duration:.1f} minutes")

        with chart_tab4:
            st.markdown("#### Popular Locations")
            st.write("Identify high-demand zones for strategic positioning")

            col1, col2 = st.columns(2)

            with col1:
                if "pickup_zip" in df.columns:
                    st.markdown("**Top 15 Pickup Locations**")
                    top_pickups = df["pickup_zip"].value_counts().head(15)
                    st.bar_chart(top_pickups, use_container_width=True)

            with col2:
                if "dropoff_zip" in df.columns:
                    st.markdown("**Top 15 Dropoff Locations**")
                    top_dropoffs = df["dropoff_zip"].value_counts().head(15)
                    st.bar_chart(top_dropoffs, use_container_width=True)

        with chart_tab5:
            st.markdown("#### Time-Based Analysis")
            st.write("Understand how trip patterns vary throughout the day")

            col1, col2 = st.columns(2)

            with col1:
                if "pickup_hour" in df.columns and "trip_distance" in df.columns:
                    st.markdown("**Average Trip Distance by Hour**")
                    avg_distance_by_hour = df.groupby("pickup_hour")[
                        "trip_distance"
                    ].mean()
                    st.line_chart(avg_distance_by_hour, use_container_width=True)

            with col2:
                if (
                    "pickup_hour" in df.columns
                    and "trip_duration_minutes" in df.columns
                ):
                    st.markdown("**Average Trip Duration by Hour**")
                    avg_duration_by_hour = df.groupby("pickup_hour")[
                        "trip_duration_minutes"
                    ].mean()
                    st.line_chart(avg_duration_by_hour, use_container_width=True)

with tab_b:
    st.markdown("### Load data from a table")
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
@st.cache_resource
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

# Read table
def read_table(table_name, conn):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
        return cursor.fetchall_arrow().to_pandas()

# Get data
warehouse_name = "your_warehouse_name"
table_name = "samples.nyctaxi.trips"

http_path = warehouse_paths[warehouse_name]
conn = get_connection(http_path)
df = read_table(table_name, conn)

# Process datetime columns
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
df["trip_duration_minutes"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
    """,
        language="python",
    )

    st.markdown("### Demand analysis: Trips by hour")
    st.code(
        """
import streamlit as st

# Count trips by hour to understand demand patterns
hourly_demand = df["pickup_hour"].value_counts().sort_index()
st.bar_chart(hourly_demand)

peak_hour = hourly_demand.idxmax()
st.info(f"Peak demand hour: {peak_hour}:00 with {hourly_demand.max()} trips")
    """,
        language="python",
    )

    st.markdown("### Revenue analysis: Average fare by hour")
    st.code(
        """
import streamlit as st

# Analyze when fares are highest
avg_fare_by_hour = df.groupby("pickup_hour")["fare_amount"].mean()
st.line_chart(avg_fare_by_hour)

best_hour = avg_fare_by_hour.idxmax()
st.success(f"Best earning hour: {best_hour}:00")
    """,
        language="python",
    )

    st.markdown("### Location analysis: Top pickup zones")
    st.code(
        """
import streamlit as st

# Identify high-demand pickup locations
top_pickups = df["pickup_zip"].value_counts().head(15)
st.bar_chart(top_pickups)
    """,
        language="python",
    )

    st.markdown("### Cumulative revenue over time")
    st.code(
        """
import streamlit as st

# Track total revenue accumulation
revenue_df = df.set_index("tpep_pickup_datetime")[["fare_amount"]].sort_index()
revenue_df["cumulative_revenue"] = revenue_df["fare_amount"].cumsum()
st.area_chart(revenue_df["cumulative_revenue"])
    """,
        language="python",
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
                    **Permissions (app service principal)**
                    * `CAN USE` on the SQL warehouse
                    * `SELECT` on the Unity Catalog table
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
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector`
                    * [Pandas](https://pypi.org/project/pandas/) - `pandas`
                    """
        )
