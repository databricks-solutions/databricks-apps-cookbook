---
name: cookbook-aiml
description: "Invoke ML models, run vector search, and connect to MCP servers from Databricks Apps. Use when the user wants to call a model serving endpoint, query a vector search index, use LLMs/embeddings, or connect to an MCP server in Dash, Streamlit, Reflex, or FastAPI."
---

# AI/ML Integration

Invoke models on [Model Serving](https://docs.databricks.com/aws/en/machine-learning/model-serving/), query [Vector Search](https://docs.databricks.com/aws/en/generative-ai/vector-search) indexes, and connect to [MCP servers](https://modelcontextprotocol.io/overview) from your Databricks App.

## Recipes

### Invoke a model serving endpoint

The SDK call is framework-agnostic. Wrap it in your framework's UI pattern.

#### Traditional ML (DataFrame input)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="custom-regression-model",
    dataframe_split={
        "columns": ["feature1", "feature2"],
        "data": [[1.5, 2.5]]
    }
)
```

#### LLM chat (messages)

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="chat-assistant-model",
    messages=[
        ChatMessage(role=ChatMessageRole.SYSTEM, content="You are a helpful assistant."),
        ChatMessage(role=ChatMessageRole.USER, content="Provide tips for Databricks Apps."),
    ],
)
```

#### LLM completion (prompt)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="llm-completions-model",
    prompt="Generate a recipe for scalable Databricks Apps.",
    temperature=0.5,
)
```

#### Embeddings

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

response = w.serving_endpoints.query(
    name="embedding-model",
    input="Databricks provides a unified analytics platform.",
)
```

### Vector search

Generate embeddings and query a vector search index:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
openai_client = w.serving_endpoints.get_open_ai_client()

def get_embeddings(text):
    response = openai_client.embeddings.create(
        model="databricks-gte-large-en", input=text
    )
    return response.data[0].embedding

def run_vector_search(prompt: str, index_name: str, columns: list[str]):
    vector = get_embeddings(prompt)
    result = w.vector_search_indexes.query_index(
        index_name=index_name,
        columns=columns,
        query_vector=vector,
        num_results=3,
    )
    return result.result.data_array
```

### Connect to an MCP server

Use Unity Catalog [HTTP connections](https://docs.databricks.com/aws/en/query-federation/http) to connect to MCP servers.

#### On-behalf-of-user

**Streamlit:**

```python
import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

token = st.context.headers.get("X-Forwarded-Access-Token")
w = WorkspaceClient(token=token, auth_type="pat")

def init_mcp_session(connection_name):
    response = w.serving_endpoints.http_request(
        conn=connection_name,
        method=ExternalFunctionRequestHttpMethod.POST,
        path="/",
        json={"jsonrpc": "2.0", "id": "init-1", "method": "initialize", "params": {}},
    )
    return response.headers.get("mcp-session-id")

session_id = init_mcp_session("github_mcp_connection")

response = w.serving_endpoints.http_request(
    conn="github_mcp_connection",
    method=ExternalFunctionRequestHttpMethod.POST,
    path="/",
    headers={"Mcp-Session-Id": session_id},
    json={"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"},
)
st.json(response.json())
```

**Reflex:**

```python
import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

class McpState(rx.State):
    response_data: str = ""

    @rx.event(background=True)
    async def send_request(self):
        headers = self.router.headers
        token = getattr(headers, "x_forwarded_access_token", "")
        w = WorkspaceClient(token=token, auth_type="pat")

        init_resp = w.serving_endpoints.http_request(
            conn="github_mcp_connection",
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            json={"jsonrpc": "2.0", "id": "init-1", "method": "initialize", "params": {}},
        )
        session_id = init_resp.headers.get("mcp-session-id")

        response = w.serving_endpoints.http_request(
            conn="github_mcp_connection",
            method=ExternalFunctionRequestHttpMethod.POST,
            path="/",
            headers={"Mcp-Session-Id": session_id},
            json={"jsonrpc": "2.0", "id": "list-1", "method": "tools/list"},
        )
        async with self:
            self.response_data = str(response.json())
```

#### Bearer token (service principal)

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

w = WorkspaceClient()

response = w.serving_endpoints.http_request(
    conn="github_connection",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/",
    headers={"Accept": "application/vnd.github+json"},
    json={"jsonrpc": "2.0", "id": "init-1", "method": "initialize", "params": {}},
)
```

## Resources

| Recipe | Resources |
|--------|-----------|
| Model serving | [Model Serving endpoint](https://docs.databricks.com/aws/en/machine-learning/model-serving/manage-serving-endpoints) |
| Vector search | [Vector Search endpoint + index](https://docs.databricks.com/aws/en/generative-ai/vector-search) |
| MCP | [Unity Catalog HTTP Connection](https://docs.databricks.com/aws/en/query-federation/http) with MCP base path |

## Permissions

| Recipe | Permissions |
|--------|-----------|
| Model serving | `CAN QUERY` on the serving endpoint |
| Vector search | `USE CATALOG`, `USE SCHEMA`, `SELECT` on the VS index |
| MCP connections | `USE CONNECTION` on the HTTP Connection |
| MCP (OBO) | Additionally configure [User authorization](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth#user-authorization) scopes |

## Dependencies

```
databricks-sdk
```

For MCP, also add `mcp[cli]`. Plus your framework package.

## Common Pitfalls

- Model serving endpoints must be in `READY` state before querying
- Vector search requires generating embeddings first (use `get_open_ai_client()`)
- MCP connections require a session initialization step; store the `mcp-session-id` for subsequent requests
- OBO tokens are only available when deployed, not during local development
