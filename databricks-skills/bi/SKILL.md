---
name: cookbook-bi
description: "Embed AI/BI dashboards and integrate Genie Spaces into Databricks Apps. Use when the user wants to embed a Databricks dashboard or build a chat interface with the Genie Conversations API in Dash, Streamlit, or Reflex."
---

# BI Integration

Embed [AI/BI dashboards](https://docs.databricks.com/aws/en/dashboards/) and integrate [Genie Spaces](https://www.databricks.com/product/ai-bi) into your Databricks App.

## Recipes

### Embed a dashboard

Embed a published AI/BI dashboard via iframe. Get the embed URL from the dashboard UI: **Share** > **Embed iframe**.

#### Dash

```python
from dash import html

iframe_source = "https://workspace.azuredatabricks.net/embed/dashboardsv3/dashboard-id"

html.Iframe(
    src=iframe_source,
    width="700px",
    height="600px",
    style={"border": "none"}
)
```

#### Streamlit

```python
import streamlit.components.v1 as components

iframe_source = "https://workspace.azuredatabricks.net/embed/dashboardsv3/dashboard-id"

components.iframe(src=iframe_source, height=600, scrolling=True)
```

#### Reflex

```python
import reflex as rx
import requests
from databricks.sdk.core import Config

def get_published_dashboards():
    cfg = Config()
    headers = {"Authorization": f"Bearer {cfg.token}"}
    url = f"{cfg.host}/api/2.0/lakeview/dashboards"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return {d.get("display_name"): d.get("dashboard_id")
            for d in data.get("dashboards", []) if d.get("published")}

class AiBiDashboardState(rx.State):
    dashboard_options: dict[str, str] = {}
    iframe_source: str = ""

    @rx.event
    def on_load(self):
        self.dashboard_options = get_published_dashboards()
        cfg = Config()
        first_id = list(self.dashboard_options.values())[0]
        self.iframe_source = f"{cfg.host}/dashboardsv3/{first_id}/published?embed=true"
```

### Chat with a Genie Space

Use the [Genie Conversations API](https://docs.databricks.com/api/workspace/genie) to let users ask natural-language questions about data. Get the Genie Space ID from the URL: `rooms/SPACE-ID?o=`.

#### Dash

```python
import pandas as pd
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
genie_space_id = "01f0023d28a71e599b5a62f4117516d4"

def get_query_result(statement_id):
    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array,
        columns=[i.name for i in result.manifest.schema.columns]
    )

def process_genie_response(response):
    for i in response.attachments:
        if i.text:
            print(f"A: {i.text.content}")
        elif i.query:
            data = get_query_result(response.query_result.statement_id)
            print(f"A: {i.query.description}")
            print(f"Data: {data}")

conversation = w.genie.start_conversation_and_wait(genie_space_id, "What are the top trips?")
process_genie_response(conversation)

follow_up = w.genie.create_message_and_wait(
    genie_space_id, conversation.conversation_id, "Show me the trend"
)
process_genie_response(follow_up)
```

#### Streamlit

```python
import streamlit as st
from databricks.sdk import WorkspaceClient
import pandas as pd

w = WorkspaceClient()
genie_space_id = "01efe16a65e21836acefb797ae6a8fe4"

def get_query_result(statement_id):
    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array,
        columns=[i.name for i in result.manifest.schema.columns]
    )

def process_genie_response(response):
    for i in response.attachments:
        if i.text:
            st.markdown(i.text.content)
        elif i.query:
            data = get_query_result(response.query_result.statement_id)
            st.dataframe(data)
            with st.expander("Show generated code"):
                st.code(i.query.query, language="sql")

if prompt := st.chat_input("Ask your question..."):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        if st.session_state.get("conversation_id"):
            conversation = w.genie.create_message_and_wait(
                genie_space_id, st.session_state.conversation_id, prompt
            )
        else:
            conversation = w.genie.start_conversation_and_wait(genie_space_id, prompt)
            st.session_state.conversation_id = conversation.conversation_id
        process_genie_response(conversation)
```

#### Reflex

```python
import reflex as rx
from databricks.sdk import WorkspaceClient
import pandas as pd

w = WorkspaceClient()
genie_space_id = "01f0023d28a71e599b5a62f4117916d4"

def get_query_result(statement_id):
    result = w.statement_execution.get_statement(statement_id)
    return pd.DataFrame(
        result.result.data_array,
        columns=[i.name for i in result.manifest.schema.columns]
    )

class GenieState(rx.State):
    conversation_id: str = ""
    prompt: str = ""

    @rx.event
    async def send_message(self):
        if self.conversation_id:
            conversation = w.genie.create_message_and_wait(
                genie_space_id, self.conversation_id, self.prompt
            )
        else:
            conversation = w.genie.start_conversation_and_wait(
                genie_space_id, self.prompt
            )
            self.conversation_id = conversation.conversation_id
        self.prompt = ""
```

## Resources

| Recipe | Resources |
|--------|-----------|
| Embed dashboard | [AI/BI dashboard](https://docs.databricks.com/aws/en/dashboards/) |
| Genie API | [Genie Space](https://www.databricks.com/what-aibi-genie), SQL warehouse, Unity Catalog tables |

## Permissions

| Recipe | Permissions |
|--------|-----------|
| Embed dashboard | `CAN VIEW` on the dashboard |
| Genie API | `SELECT` on UC tables, `CAN USE` SQL warehouse, `CAN VIEW` Genie Space |

A workspace admin must enable dashboard embedding in **Security settings** for specific domains (e.g. `databricksapps.com`) or all domains.

## Dependencies

```
databricks-sdk
pandas
```

Plus your framework package. Reflex Genie also needs `requests` for dashboard listing.
