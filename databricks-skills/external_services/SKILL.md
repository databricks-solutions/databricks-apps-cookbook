---
name: cookbook-external-services
description: "Connect Databricks Apps to external services using Unity Catalog HTTP connections and retrieve Databricks secrets. Use when the user needs to call external APIs (GitHub, Jira, Slack), set up MCP connections, or access secrets from Dash, Streamlit, or Reflex apps."
---

# External Services

Connect to external APIs using Unity Catalog [HTTP connections](https://docs.databricks.com/aws/en/query-federation/http) and retrieve [Databricks secrets](https://docs.databricks.com/en/security/secrets/index.html) for secure credential management.

## Recipes

### External HTTP connections

Use UC-managed HTTP connections for governed access to external services (GitHub, Jira, Slack, or any MCP/non-MCP server).

#### On-behalf-of-user (OAuth U2M)

Uses the end user's identity to call the external service:

**Dash:**

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod
from flask import request

token = request.headers.get("x-forwarded-access-token")
w = WorkspaceClient(token=token, auth_type="pat")

response = w.serving_endpoints.http_request(
    conn="github_u2m",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/user",
    headers={"Accept": "application/vnd.github+json"},
)
print(response.json())
```

**Streamlit:**

```python
import streamlit as st
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

token = st.context.headers.get("X-Forwarded-Access-Token")
w = WorkspaceClient(token=token, auth_type="pat")

response = w.serving_endpoints.http_request(
    conn="github_u2m",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/user",
    headers={"Accept": "application/vnd.github+json"},
)
st.json(response.json())
```

**Reflex:**

```python
import reflex as rx
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

class ExternalConnectionsState(rx.State):
    response_data: str = ""

    @rx.event
    async def run(self):
        headers = self.router.headers
        token = getattr(headers, "x_forwarded_access_token", "")
        w = WorkspaceClient(token=token, auth_type="pat")

        response = w.serving_endpoints.http_request(
            conn="github_u2m",
            method=ExternalFunctionRequestHttpMethod.GET,
            path="/user",
            headers={"Accept": "application/vnd.github+json"},
        )
        self.response_data = str(response.json())
```

#### Bearer token (service principal)

Uses the app's service principal identity:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ExternalFunctionRequestHttpMethod

w = WorkspaceClient()

response = w.serving_endpoints.http_request(
    conn="github_connection",
    method=ExternalFunctionRequestHttpMethod.GET,
    path="/traffic/views",
    headers={"Accept": "application/vnd.github+json"},
)
```

### Retrieve a secret

Access [Databricks secrets](https://docs.databricks.com/en/security/secrets/index.html) for API keys and credentials:

```python
import base64
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_secret(scope: str, key: str) -> str:
    secret_response = w.secrets.get_secret(scope=scope, key=key)
    return base64.b64decode(secret_response.value).decode("utf-8")

api_key = get_secret("my_scope", "api_key")
```

## Resources

| Recipe | Resources |
|--------|-----------|
| HTTP connections | [Unity Catalog HTTP Connection](https://docs.databricks.com/aws/en/query-federation/http) |
| Secrets | [Secret scope](https://docs.databricks.com/aws/en/security/secrets/) |

## Permissions

| Recipe | Permissions |
|--------|-----------|
| HTTP connections | `USE CONNECTION` on the HTTP Connection |
| HTTP connections (OBO) | Additionally configure [User authorization](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth#user-authorization) scopes |
| Secrets | `CAN READ` on the secret scope |

## Dependencies

```
databricks-sdk
```

Plus your framework package (`dash`, `streamlit`, or `reflex`).

## Common Pitfalls

- OBO tokens (`x-forwarded-access-token`) are only available when deployed to Databricks Apps, not locally
- Secret values are base64-encoded; always decode with `base64.b64decode()`
- For MCP servers, initialize a session first to get a `mcp-session-id` header for subsequent requests
