---
name: cookbook-visualizations
description: "Create charts, graphs, and map visualizations in Databricks Apps. Use when the user wants to display data as bar charts, line charts, area charts, or interactive maps in Streamlit, Dash, or Reflex apps."
---

# Visualizations

Create charts, graphs, and interactive maps in your Databricks App using data from Unity Catalog tables.

## Recipes

### Charts (bar, line, area)

#### Streamlit

Streamlit has built-in chart components. Load data from a UC table, then visualize:

```python
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
import pandas as pd

cfg = Config()

@st.cache_resource(ttl=300)
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name, conn):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
        return cursor.fetchall_arrow().to_pandas()

conn = get_connection("/sql/1.0/warehouses/xxxxxx")
df = read_table("samples.nyctaxi.trips", conn)

df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour

# Bar chart: trips by hour
hourly_demand = df["pickup_hour"].value_counts().sort_index()
st.bar_chart(hourly_demand)

# Line chart: average fare by hour
avg_fare = df.groupby("pickup_hour")["fare_amount"].mean()
st.line_chart(avg_fare)

# Area chart: cumulative revenue
revenue = df.set_index("tpep_pickup_datetime")[["fare_amount"]].sort_index()
revenue["cumulative"] = revenue["fare_amount"].cumsum()
st.area_chart(revenue["cumulative"])
```

#### Dash

Use [Plotly](https://plotly.com/python/) with Dash for interactive charts:

```python
from dash import dcc
import plotly.express as px
import pandas as pd

# Assuming df is loaded from a UC table (see tables skill)
fig = px.bar(df, x="pickup_hour", y="trip_count", title="Trips by Hour")
dcc.Graph(figure=fig)

fig_line = px.line(df, x="pickup_hour", y="avg_fare", title="Average Fare")
dcc.Graph(figure=fig_line)
```

#### Reflex

```python
import reflex as rx

# Reflex uses recharts under the hood
rx.recharts.bar_chart(
    rx.recharts.bar(data_key="count", fill="#8884d8"),
    rx.recharts.x_axis(data_key="hour"),
    rx.recharts.y_axis(),
    data=chart_data,
    width="100%",
    height=300,
)
```

### Map display

#### Streamlit

Display geographic data with `st.map` or use [Folium](https://python-visualization.github.io/folium/) for interactive drawing:

```python
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw

# Simple map from a DataFrame with lat/lon columns
st.map(df, latitude="latitude", longitude="longitude")

# Interactive map with drawing tools (Folium)
m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)
draw = Draw(
    draw_options={
        "marker": True,
        "polygon": True,
        "polyline": True,
        "rectangle": True,
        "circle": True,
        "circlemarker": False,
    },
    edit_options={"edit": True},
)
draw.add_to(m)
output = st_folium(m, width=700, height=500)

if output["last_active_drawing"] and "geometry" in output["last_active_drawing"]:
    geometry = output["last_active_drawing"]["geometry"]
    st.json(geometry)
```

#### Dash

```python
from dash import dcc
import plotly.express as px

fig = px.scatter_mapbox(
    df, lat="latitude", lon="longitude",
    zoom=10, mapbox_style="open-street-map"
)
dcc.Graph(figure=fig)
```

## Resources

- [SQL warehouse](https://docs.databricks.com/aws/en/compute/sql-warehouse/) (for loading data)
- [Unity Catalog table](https://docs.databricks.com/aws/en/tables/) (data source)

## Permissions

- `CAN USE` on the SQL warehouse
- `SELECT` on the Unity Catalog table

## Dependencies

| Framework | Packages |
|-----------|----------|
| Streamlit | `streamlit`, `databricks-sdk`, `databricks-sql-connector`, `pandas` |
| Streamlit + maps | Add `streamlit-folium` |
| Dash | `dash`, `plotly`, `databricks-sdk`, `databricks-sql-connector`, `pandas` |
| Reflex | `reflex`, `databricks-sdk`, `pandas` |

## Common Pitfalls

- Streamlit's `st.map` requires columns named `latitude`/`longitude` (or `lat`/`lon`) -- rename if needed
- Folium maps require `streamlit-folium` as an extra dependency
- Limit query results (e.g. `LIMIT 1000`) to avoid rendering performance issues
