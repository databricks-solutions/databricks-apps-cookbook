---
name: cookbook-authentication
description: "Implement authentication in Databricks Apps: get current user info, on-behalf-of-user (OBO) auth, service principal auth, and OAuth patterns. Use when the user asks about auth, user tokens, service principals, OAuth, or OBO in Dash, Streamlit, Reflex, or FastAPI."
---

# Authentication

Databricks Apps supports two auth models: **app auth** (service principal) and **user auth** (on-behalf-of-user). Choose based on whether operations should run as the app or as the logged-in user.

| Model | Identity | When to Use |
|-------|----------|-------------|
| App auth (service principal) | Auto-injected via `Config()` | Default. Data access with app-level permissions |
| User auth (OBO) | `x-forwarded-access-token` header | Per-user permissions, audit trails |

## Recipes

### Get current user info

Read HTTP headers injected by the Databricks Apps proxy to identify the logged-in user.

#### Dash

```python
from flask import request

headers = request.headers
email = headers.get("X-Forwarded-Email")
username = headers.get("X-Forwarded-Preferred-Username")
user = headers.get("X-Forwarded-User")
ip = headers.get("X-Real-Ip")
```

#### Streamlit

```python
import streamlit as st
from databricks.sdk import WorkspaceClient

headers = st.context.headers
email = headers.get("X-Forwarded-Email")
username = headers.get("X-Forwarded-Preferred-Username")
user_access_token = headers.get("X-Forwarded-Access-Token")

if user_access_token:
    w = WorkspaceClient(token=user_access_token, auth_type="pat")
    current_user = w.current_user.me()
    st.write(f"Display Name: {current_user.display_name}")
    st.write(f"Groups: {len(current_user.groups) if current_user.groups else 0}")
```

#### Reflex

```python
import reflex as rx
from databricks.sdk import WorkspaceClient

class UserState(rx.State):
    user_info: dict = {}

    @rx.event
    def load_user(self):
        headers = self.router.headers
        token = getattr(headers, "x_forwarded_access_token", "")
        if token:
            w = WorkspaceClient(token=token, auth_type="pat")
            user = w.current_user.me()
            self.user_info = {
                "name": user.display_name,
                "email": user.user_name,
            }
```

### On-behalf-of-user (OBO) authentication

Run queries using the end user's permissions via their forwarded access token.

#### Streamlit

```python
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

def get_user_token():
    return st.context.headers["X-Forwarded-Access-Token"]

@st.cache_resource(ttl=300)
def connect_with_obo(http_path, user_token):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        access_token=user_token,
    )

user_token = get_user_token()
conn = connect_with_obo("/sql/1.0/warehouses/xxxxxx", user_token)

with conn.cursor() as cursor:
    cursor.execute("SELECT * FROM samples.nyctaxi.trips LIMIT 10")
    df = cursor.fetchall_arrow().to_pandas()
    st.dataframe(df)
```

#### Reflex

```python
import reflex as rx
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

class OboQueryState(rx.State):
    results: list = []

    @rx.event(background=True)
    async def run_query(self):
        headers = self.router.headers
        token = getattr(headers, "x_forwarded_access_token", "")
        conn = sql.connect(
            server_hostname=cfg.host,
            http_path="/sql/1.0/warehouses/xxxxxx",
            access_token=token,
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM samples.nyctaxi.trips LIMIT 10")
            async with self:
                self.results = cursor.fetchall_arrow().to_pandas().values.tolist()
```

### Service principal auth (app auth)

This is the default. `Config()` auto-detects credentials from the environment (`DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`).

```python
from databricks.sdk.core import Config
from databricks import sql

cfg = Config()

conn = sql.connect(
    server_hostname=cfg.host,
    http_path="/sql/1.0/warehouses/xxxxxx",
    credentials_provider=lambda: cfg.authenticate,
)
```

For the SDK client:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()  # auto-configured from environment
```

### FastAPI: Connecting from different contexts

FastAPI apps support multiple authentication contexts:

#### From deployed app (service principal)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()  # uses auto-injected DATABRICKS_HOST + client credentials
```

#### From external service (M2M)

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(
    host="https://workspace.cloud.databricks.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

#### From local development

```bash
databricks auth login --host https://workspace.cloud.databricks.com
```

Then in code:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient(profile="DEFAULT")
```

#### OAuth2 Bearer for API routes

FastAPI endpoints on Databricks Apps must be under the `/api` prefix and require Bearer token auth:

```python
from fastapi import FastAPI

app = FastAPI()

# All routes under /api are protected by Databricks Apps OAuth2
@app.get("/api/v1/data")
async def get_data():
    return {"message": "authenticated"}
```

## Available HTTP Headers

| Header | Description | Requires OBO |
|--------|-------------|-------------|
| `X-Forwarded-Email` | User's email | No |
| `X-Forwarded-Preferred-Username` | Username | No |
| `X-Forwarded-User` | User ID | No |
| `X-Real-Ip` | Client IP | No |
| `X-Forwarded-Access-Token` | User's OAuth token | Yes |

## Enabling OBO

OBO requires workspace admin to enable [on-behalf-of-user authentication](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development#-using-the-databricks-apps-authorization-model) for the app. Without it, only basic headers (email, username) are available.

## Resources

| Auth model | Resources |
|-----------|-----------|
| App auth | None (auto-configured) |
| OBO + SQL | [SQL warehouse](https://docs.databricks.com/aws/en/compute/sql-warehouse/) |

## Permissions

| Auth model | Permissions |
|-----------|-----------|
| App auth | Service principal needs permissions on accessed resources |
| OBO | End user's permissions apply; user needs `CAN USE` on SQL warehouse |

## Dependencies

```
databricks-sdk
databricks-sql-connector
```

Plus your framework package.

## Common Pitfalls

- `X-Forwarded-Access-Token` is only present when deployed with OBO enabled; it's missing during local dev
- Without OBO, `w.current_user.me()` returns the service principal, not the logged-in user
- Never hardcode tokens; always use `Config()` for service principal auth
- FastAPI routes must be under `/api` prefix to receive Bearer token authentication
- Cache OBO connections per user token to avoid connection exhaustion
