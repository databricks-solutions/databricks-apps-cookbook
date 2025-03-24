import streamlit as st
from databricks.sdk import WorkspaceClient
import pandas as pd

w = WorkspaceClient()

def get_all_alerts(): 
    alerts = [alert.__dict__ for alert in w.alerts.list()]
    return pd.DataFrame(alerts)

st.header("List alert", divider=True)
st.subheader("Enable users to display all alerts")
st.write("This receipt enables users to display all alerts.")

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippet**", "**Requirements**"])

with tab_a:
    st.write("""### See all alerts""")
    st.dataframe(get_all_alerts())

table = [
    {
        "type": "Get alerts",
        "param": "",
        "description": "Get all alerts",
        "code": """
        ```python
        def get_all_alerts(): 
            alerts = [alert.__dict__ for alert in w.alerts.list()]
            return pd.DataFrame(alerts)
        ```
        """,
    },
]


with tab_b:
    for i, row in enumerate(table):
        with st.expander(f"**{row['type']} ({row['param']})**", expanded=(i == 0)):
            st.markdown(f"**Description**: {row['description']}")
            st.markdown(row["code"])
