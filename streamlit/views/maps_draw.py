
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import Draw



st.header("Collect user geo input", divider=True)
st.subheader("Enable user to select geo input")
st.write("This receipt enables users to pick geo points or draw geofences to futher be used.")

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    choice=st.selectbox("### Select an option",['Points', 'Geofences','Polyline', 'Rectangle','Circle'])

    col1, col2 = st.columns(2)

    with col1: 

        st.write("## Select a map input")
        m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
        draw = Draw(
            draw_options={
                "polyline": True if choice=='Polyline' else False,
                "rectangle":  True if choice=='Rectangle' else False,
                "circle":  True if choice=='Circle' else False,
                "marker": True if choice=='Points' else False ,
                "circlemarker": False,
                "polygon": True if choice=='Geofences' else False,  
            },
            edit_options={"edit": True},
        )
        draw.add_to(m)
        output = st_folium(m, width=700, height=500)

        st.write("For usage of the app, select a point on the map.")
        with st.expander("Click to see the last active selected map input", expanded=False):
            if output["last_active_drawing"] and "geometry" in output["last_active_drawing"]:
                st.json(output["last_active_drawing"]["geometry"])


table = [
    {
        "type": "User Input for points",
        "param": "",
        "description": "User input for long, lat.",
        "code": """
        ```python
            m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
            draw = Draw(
                draw_options={
                    "polyline": False,
                    "rectangle": False,
                    "circle": False,
                    "marker": True,
                    "circlemarker": False,
                    "polygon":False,  
                },
                edit_options={"edit": True},
            )
            draw.add_to(m)
            output = st_folium(m, width=700, height=500)
        ```
        """,
    },
    {
        "type": "User input for geofences",
        "param": "",
        "description": "Enable users to draw geo fences",
        "code": """
        ```python
         m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
            draw = Draw(
                draw_options={
                    "polyline": False,
                    "rectangle": False,
                    "circle": False,
                    "marker": False,
                    "circlemarker": False,
                    "polygon":True,  
                },
                edit_options={"edit": True},
            )
            draw.add_to(m)
            output = st_folium(m, width=700, height=500)
        ```
        """,
    },
    {
        "type": "User input for polylines",
        "param": "",
        "description": "Enable users to draw polylines",
        "code": """
        ```python
         m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
            draw = Draw(
                draw_options={
                    "polyline": True,
                    "rectangle": False,
                    "circle": False,
                    "marker": False,
                    "circlemarker": False,
                    "polygon":False,  
                },
                edit_options={"edit": True},
            )
            draw.add_to(m)
            output = st_folium(m, width=700, height=500)
        ```
        """,
    },
    {
        "type": "User input for rectangles",
        "param": "",
        "description": "Enable users to draw rectangles",
        "code": """
        ```python
         m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
            draw = Draw(
                draw_options={
                    "polyline": False,
                    "rectangle": True,
                    "circle": False,
                    "marker": False,
                    "circlemarker": False,
                    "polygon":False,  
                },
                edit_options={"edit": True},
            )
            draw.add_to(m)
            output = st_folium(m, width=700, height=500)
        ```
        """,
    },
    {
        "type": "User input for circles",
        "param": "",
        "description": "Enable users to draw circles",
        "code": """
        ```python
         m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
            draw = Draw(
                draw_options={
                    "polyline": False,
                    "rectangle": False,
                    "circle": True,
                    "marker": False,
                    "circlemarker": False,
                    "polygon":False,  
                },
                edit_options={"edit": True},
            )
            draw.add_to(m)
            output = st_folium(m, width=700, height=500)
        ```
        """,
    },
    {
        "type": "User input for markers",
        "param": "",
        "description": "Enable users to draw markers",
        "code": """
        ```python
         m = folium.Map(location=[37.7749, -122.4194], zoom_start=13)  # Example: San Francisco
            draw = Draw(
                draw_options={
                    "polyline": False,
                    "rectangle": False,
                    "circle": False,
                    "marker": True,
                    "circlemarker": False,
                    "polygon":False,  
                },
                edit_options={"edit": True},
            )
            draw.add_to(m)
            output = st_folium(m, width=700, height=500)
        ```
        """,
    },
        {
        "type": "Output user input",
        "param": "",
        "description": "Display user input as json.",
        "code": """
        ```python
            st.write("For usage of the app, select a point on the map.")
            with st.expander("Click to see the last active selected map input", expanded=False):
                if output["last_active_drawing"] and "geometry" in output["last_active_drawing"]:
                    st.json(output["last_active_drawing"]["geometry"])

        ```
        """,
    },

]

with tab_b:
    for i, row in enumerate(table):
        with st.expander(f"**{row['type']} ({row['param']})**", expanded=(i == 0)):
            st.markdown(f"**Description**: {row['description']}")
            st.markdown(row["code"])
