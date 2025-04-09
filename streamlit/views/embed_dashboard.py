import streamlit as st
import streamlit.components.v1 as components
import requests
from databricks.sdk.core import Config

st.header("Data Visualization", divider=True)
st.subheader("AI/BI Dashboard")
st.write(
    """
    This recipe uses [Databricks AI/BI](https://www.databricks.com/product/ai-bi) to embed a dashboard into a Databricks App. 
    """
)
tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])


with tab_a:


    cfg = Config()

    host = cfg.host

    token = list(cfg.authenticate().values())[0].split(" ")[1]
    url = f"{host}/api/2.0/lakeview/dashboards"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    dashboards = response.json()
    dashboard_paths = {dashboard['display_name']: dashboard['dashboard_id'] for dashboard in dashboards['dashboards']}

    published_dashboards = []

    for dashboard in dashboards['dashboards']:
        dashboard_id = dashboard['dashboard_id']
        
        published_url = f"{host}/api/2.0/lakeview/dashboards/{dashboard_id}/published"
        response = requests.get(published_url, headers=headers)
    
        if response.status_code == 200:
            published_dashboards.append((dashboard['display_name'], dashboard['dashboard_id']))
            print( dashboard['display_name'] + ' ' + dashboard['dashboard_id'])
    final_published_dashboards = {k: v for k, v in published_dashboards }

    #st.info(final_published_dashboards)
    iframe_source_temp = st.selectbox(
        "Select your AI/BI Dashboard:", [""] + list(final_published_dashboards.keys()),
        help="Dashboard list populated from your workspace using app service principal.",
    )
 
    dashboard_id = final_published_dashboards.get(iframe_source_temp)

    if iframe_source_temp and iframe_source_temp != "":
        iframe_source = f"{host}/embed/dashboardsv3/{dashboard_id}"
        #st.info(iframe_source)
        components.iframe(src=iframe_source, width=700, height=600, scrolling=True)

with tab_b:
    st.code(
        """
        import streamlit.components.v1 as components
        
        iframe_source = "https://workspace.azuredatabricks.net/embed/dashboardsv3/dashboard-id"

        components.iframe(
            src=iframe_source,
            width=700,
            height=600,
            scrolling=True
        )
        """
    )

with tab_c:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `CAN VIEW` permission on the dashboard
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * SQL Warehouse
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)

    st.warning(
        "A workspace admin needs to enable dashboard embedding in the Security settings of your Databricks workspace for specific domains (e.g., databricksapps.com) or all domains for this sample to work.",
        icon="⚠️",
    )
