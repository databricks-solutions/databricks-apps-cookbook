---
name: cookbook-unity-catalog
description: "Browse Unity Catalog objects (catalogs, schemas) from Databricks Apps. Use when the user wants to list catalogs, explore schemas, or build a catalog browser in a Streamlit or Reflex app."
---

# Unity Catalog Browser

List and browse [Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/) objects (catalogs and schemas) from your Databricks App using the Databricks SDK.

## Recipes

### List catalogs and schemas

#### Streamlit

```python
import streamlit as st
import pandas as pd
import datetime
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_catalogs():
    catalogs = w.catalogs.list()
    data = []
    for catalog in catalogs:
        data.append({
            "Name": catalog.name,
            "Owner": catalog.owner,
            "Comment": catalog.comment,
            "Created": datetime.datetime.fromtimestamp(catalog.created_at / 1000),
        })
    return pd.DataFrame(data)

def get_schemas(catalog_name):
    schemas = w.schemas.list(catalog_name=catalog_name, max_results=10)
    data = []
    for schema in schemas:
        data.append({
            "Name": schema.full_name,
            "Owner": schema.owner,
            "Comment": schema.comment,
        })
    return pd.DataFrame(data)

if st.button("Get catalogs"):
    catalogs_df = get_catalogs()
    st.dataframe(catalogs_df)

    catalog_names = catalogs_df["Name"].tolist()
    selected = st.selectbox("Choose a catalog", options=catalog_names)

    if st.button("Get schemas"):
        schemas_df = get_schemas(selected)
        st.dataframe(schemas_df)
```

#### Reflex

```python
import reflex as rx
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

class CatalogState(rx.State):
    catalog_data: list[list[str]] = []
    schema_data: list[list[str]] = []
    catalog_names: list[str] = []
    selected_catalog: str = ""

    @rx.event
    def load_catalogs(self):
        catalogs = w.catalogs.list()
        self.catalog_data = [
            [c.name, c.owner or "", c.comment or ""]
            for c in catalogs
        ]
        self.catalog_names = [c.name for c in catalogs]

    @rx.event
    def load_schemas(self):
        schemas = w.schemas.list(catalog_name=self.selected_catalog)
        self.schema_data = [
            [s.name, s.owner or "", s.comment or ""]
            for s in schemas
        ]
```

#### Dash

```python
from databricks.sdk import WorkspaceClient
import pandas as pd
import datetime

w = WorkspaceClient()

def get_catalogs():
    catalogs = w.catalogs.list()
    return pd.DataFrame([{
        "Name": c.name,
        "Owner": c.owner,
        "Comment": c.comment,
        "Created": datetime.datetime.fromtimestamp(c.created_at / 1000),
    } for c in catalogs])

def get_schemas(catalog_name):
    schemas = w.schemas.list(catalog_name=catalog_name, max_results=10)
    return pd.DataFrame([{
        "Name": s.full_name,
        "Owner": s.owner,
        "Comment": s.comment,
    } for s in schemas])
```

## Resources

- Unity Catalog enabled workspace

## Permissions

The app service principal needs:
- `USE CATALOG` on catalogs to list
- `USE SCHEMA` on schemas to browse

To list all catalogs, the [metastore admin](https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/admin-privileges#metastore-admins) role is required. Otherwise only catalogs the service principal has privileges on are returned.

## Dependencies

```
databricks-sdk
pandas
```

Plus your framework package (`dash`, `streamlit`, or `reflex`).
