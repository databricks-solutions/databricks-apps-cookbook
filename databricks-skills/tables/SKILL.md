---
name: cookbook-tables
description: "Read and write Delta tables and connect to Lakebase (OLTP PostgreSQL) from Databricks Apps. Use when the user needs to query UC tables, edit table data, or use Lakebase for transactional workloads in Dash, Streamlit, Reflex, or FastAPI."
---

# Tables and Lakebase

Read and write [Unity Catalog tables](https://docs.databricks.com/aws/en/tables/) via SQL warehouse, and connect to [Lakebase](https://docs.databricks.com/aws/en/oltp/) (managed PostgreSQL) for transactional workloads.

## Recipes

### Read a Delta table

Uses the [Databricks SQL Connector](https://docs.databricks.com/en/dev-tools/python-sql-connector.html) via a SQL warehouse.

#### Dash

```python
from functools import lru_cache
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

@lru_cache(maxsize=1)
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name, conn):
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

conn = get_connection("/sql/1.0/warehouses/xxxxxx")
df = read_table("catalog.schema.table", conn)
```

#### Streamlit

```python
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

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
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

conn = get_connection("/sql/1.0/warehouses/xxxxxx")
df = read_table("catalog.schema.table", conn)
st.dataframe(df)
```

#### FastAPI

```python
from fastapi import APIRouter
from databricks import sql
from databricks.sdk.core import Config

router = APIRouter()
cfg = Config()

def get_connection():
    return sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{os.getenv('DATABRICKS_WAREHOUSE_ID')}",
        credentials_provider=lambda: cfg.authenticate,
    )

@router.get("/data/{table_name}")
async def read_table(table_name: str):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        return cursor.fetchall_arrow().to_pandas().to_dict(orient="records")
```

### Edit a Delta table (INSERT OVERWRITE)

#### Dash / Streamlit (common pattern)

```python
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
    with conn.cursor() as cursor:
        rows = list(df.itertuples(index=False, name=None))
        if not rows:
            return
        cols = list(df.columns)
        params = {}
        values_parts = []
        p = 0
        for row in rows:
            ph = []
            for v in row:
                key = f"p{p}"
                ph.append(f":{key}")
                params[key] = v
                p += 1
            values_parts.append("(" + ",".join(ph) + ")")
        col_sql = ",".join(cols)
        vals_sql = ",".join(values_parts)
        cursor.execute(
            f"INSERT OVERWRITE {table_name} ({col_sql}) VALUES {vals_sql}",
            params,
        )
```

### Connect to Lakebase (OLTP PostgreSQL)

Uses OAuth token-based auth with connection pooling via `psycopg`.

#### Dash / Streamlit / Reflex

```python
import uuid
import pandas as pd
from databricks.sdk import WorkspaceClient
import psycopg
from psycopg_pool import ConnectionPool

w = WorkspaceClient()

class RotatingTokenConnection(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo="", **kwargs):
        kwargs["password"] = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()),
            instance_names=[kwargs.pop("_instance_name")]
        ).token
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)

def build_pool(instance_name, host, user, database):
    return ConnectionPool(
        conninfo=f"host={host} dbname={database} user={user}",
        connection_class=RotatingTokenConnection,
        kwargs={"_instance_name": instance_name},
        min_size=1, max_size=5, open=True,
    )

def query_df(pool, sql_query):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_query)
            if cur.description is None:
                return pd.DataFrame()
            cols = [d.name for d in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)

instance_name = "my_instance"
user = w.current_user.me().user_name
host = w.database.get_database_instance(name=instance_name).read_write_dns

pool = build_pool(instance_name, host, user, "databricks_postgres")
df = query_df(pool, "SELECT * FROM public.my_table LIMIT 10")
```

#### FastAPI (async with SQLAlchemy)

FastAPI uses async SQLAlchemy with token refresh for Lakebase:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_token(instance_name):
    return w.database.generate_database_credential(
        request_id=str(uuid.uuid4()),
        instance_names=[instance_name]
    ).token

engine = create_async_engine(
    "postgresql+asyncpg://user@host:5432/database",
    connect_args={"ssl": "require"},
)
```

See the FastAPI cookbook source for the full token-refresh and health-check implementation.

## When to Use What

| Use Case | Backend |
|----------|---------|
| Analytical queries, dashboards, reporting | SQL warehouse + Delta tables |
| Transactional reads/writes, low latency | Lakebase (PostgreSQL) |
| Form submissions, CRUD apps | Lakebase (PostgreSQL) |

## Resources

| Recipe | Resources |
|--------|-----------|
| Delta tables | [SQL warehouse](https://docs.databricks.com/aws/en/compute/sql-warehouse/), [UC table](https://docs.databricks.com/aws/en/tables/) |
| Lakebase | [Lakebase instance](https://docs.databricks.com/aws/en/oltp/) (PostgreSQL) |

## Permissions

| Recipe | Permissions |
|--------|-------------|
| Read table | `SELECT` on UC table, `CAN USE` SQL warehouse |
| Edit table | `MODIFY` on UC table, `CAN USE` SQL warehouse |
| Lakebase | PostgreSQL role with `CONNECT`, `USAGE`, `SELECT`/`INSERT` grants |

The Lakebase instance must be in your [App resources](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources). A PostgreSQL role for the service principal is required -- see [Lakebase roles guide](https://docs.databricks.com/aws/en/oltp/pg-roles).

## Dependencies

| Backend | Packages |
|---------|----------|
| SQL warehouse | `databricks-sdk`, `databricks-sql-connector`, `pandas` |
| Lakebase (sync) | `databricks-sdk`, `psycopg[binary]`, `psycopg-pool`, `pandas` |
| Lakebase (async/FastAPI) | `databricks-sdk`, `sqlalchemy`, `asyncpg` |

## Common Pitfalls

- Use `@st.cache_resource` (Streamlit) or `@lru_cache` (Dash) to cache DB connections
- Lakebase OAuth tokens expire; use `RotatingTokenConnection` or periodic refresh
- Always use `sslmode=require` for Lakebase connections
- `psycopg` and `asyncpg` are NOT pre-installed in the app runtime; add to `requirements.txt`
- `INSERT OVERWRITE` replaces all data in the table; use `INSERT INTO` for appending
