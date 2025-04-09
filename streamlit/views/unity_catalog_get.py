import pandas as pd
import streamlit as st
import datetime
from databricks.sdk import WorkspaceClient


w = WorkspaceClient()


def get_catalogs():
    catalogs = w.catalogs.list()

    catalogs_data = []
    for catalog in catalogs:
        catalogs_data.append(
            {
                "Catalog name": catalog.name,
                "Owner": catalog.owner,
                "Comment": catalog.comment,
                "Created at": datetime.datetime.fromtimestamp(
                    catalog.created_at / 1000
                ),
                "Updated at": datetime.datetime.fromtimestamp(
                    catalog.updated_at / 1000
                ),
            }
        )
    return pd.DataFrame(catalogs_data)


def get_catalog_names():
    catalogs = w.catalogs.list()
    return [catalog.name for catalog in catalogs]


def get_schemas_for_catalog(catalog_name):
    schema_data = []
    schemas = w.schemas.list(catalog_name=catalog_name, max_results=10)
    for schema in schemas:
        schema_data.append(
            {
                "Catalog name": schema.catalog_name,
                "Catalog type": schema.catalog_type,
                "Schema name": schema.full_name,
                "Owner": schema.owner,
                "Comment": schema.comment,
                "Created at": datetime.datetime.fromtimestamp(schema.created_at / 1000)
                if schema.created_at
                else None,
                "Updated at": datetime.datetime.fromtimestamp(schema.updated_at / 1000)
                if schema.updated_at
                else None,
                "Effective predictive optimization": schema.effective_predictive_optimization_flag,
                "Properties": schema.properties,
            }
        )
    return pd.DataFrame(schema_data)


st.header(body="Unity Catalog", divider=True)
st.subheader("Get catalog and schema information")
st.write("This receipt lists metadata for catalogs and schemas in Unity Catalog.")

tab_a, tab_b, tab_c = st.tabs(["**Try it**", "**Code snippets**", "**Requirements**"])

with tab_a:
    if st.button("Get catalogs"):
        st.session_state["catalogs_df"] = get_catalogs()
        st.session_state["catalog_names"] = get_catalog_names()

    if "catalogs_df" in st.session_state:
        st.write("### Catalogs")
        st.dataframe(st.session_state["catalogs_df"])

        st.write("### Select a Catalog to View its Schemas")
        selected_catalog = st.selectbox(
            "Choose a catalog", options=st.session_state["catalog_names"]
        )

        if st.button("Get schemas for selected catalog"):
            schemas_df = get_schemas_for_catalog(selected_catalog)
            st.write(f"### Schemas for {selected_catalog}")
            if not schemas_df.empty:
                st.dataframe(schemas_df)
            else:
                st.info(f"No schemas found in the catalog '{selected_catalog}'")


table = [
    {
        "type": "Get Catalog",
        "param": "get_catalog",
        "description": "Get the catalogs.",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient

        
        w = WorkspaceClient()

        def get_catalogs():
            catalogs = w.catalogs.list()
            # Parse metadata into a list of dictionaries
            catalogs_data = []
            for catalog in catalogs:
                catalogs_data.append({
                    "Catalog Name": catalog.name,
                    "Owner": catalog.owner,
                    "Comment": catalog.comment,
                    "Created At": datetime.datetime.fromtimestamp(catalog.created_at/1000),
                    "Updated At": datetime.datetime.fromtimestamp(catalog.updated_at/1000),
                })    
            return pd.DataFrame(catalogs_data)
        st.write('### Databricks Catalogs')
        st.dataframe(get_catalogs())
        ```
        """,
    },
    {
        "type": "Get Schemas for Selected Catalog",
        "param": "get_schemas_for_catalog",
        "description": "Get the schemas for a specific catalog",
        "code": """
        ```python
        from databricks.sdk import WorkspaceClient
        

        w = WorkspaceClient()
        
        def get_catalog_names():
            catalogs = w.catalogs.list()
            return [catalog.name for catalog in catalogs]
                
        def get_schemas_for_catalog(catalog_name):
            schema_data = []
            schemas = w.schemas.list(catalog_name=catalog_name, max_results=10)
            for schema in schemas:
                schema_data.append({
                    "Catalog Name": schema.catalog_name,
                    "Catalog Type": schema.catalog_type,
                    "Schema Name": schema.full_name,
                    "Owner": schema.owner,
                    "Comment": schema.comment,
                    "Created At": datetime.datetime.fromtimestamp(schema.created_at/1000) if schema.created_at else None,
                    "Updated At": datetime.datetime.fromtimestamp(schema.updated_at/1000) if schema.updated_at else None,
                    "Effective Predictive Optimization": schema.effective_predictive_optimization_flag,
                    "Properties": schema.properties
                })
            return pd.DataFrame(schema_data)
            
        # In the UI:
        selected_catalog = st.selectbox("Choose a catalog", options=get_catalog_names())
        if st.button("Get Schemas"):
            schemas = get_schemas_for_catalog(selected_catalog)
            st.dataframe(schemas)
        ```
        """,
    },
]

with tab_b:
    for i, row in enumerate(table):
        with st.expander(f"**{row['type']} ({row['param']})**", expanded=(i == 0)):
            st.markdown(f"**Description**: {row['description']}")
            st.markdown(row["code"])

with tab_c:
    st.info("""
    To list all catalogs, you need the [metastore admin](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/admin-privileges#metastore-admins) role.
    Otherwise, only catalogs for which you have the `USE_CATALOG` permission will be retrieved. 
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
                    **Permissions (app service principal)**
                    * `USE_CATALOG` on the Unity Catalog catalogs to list
                    * `USE_SCHEMA` on the schemas you want to view
                    """)
    with col2:
        st.markdown("""
                    **Databricks resources**
                    * Unity Catalog enabled workspace
                    """)
    with col3:
        st.markdown("""
                    **Dependencies**
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Streamlit](https://pypi.org/project/streamlit/) - `streamlit`
                    """)
