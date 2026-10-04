---
name: cookbook-compute
description: "Connect Databricks Apps to shared clusters or serverless compute using Databricks Connect. Use when the user needs to run Spark SQL or Python on a cluster from a Dash, Streamlit, or Reflex app."
---

# Connect to Compute

Use [Databricks Connect](https://docs.databricks.com/en/dev-tools/databricks-connect/python/index.html) to execute Python or SQL code on a shared cluster or serverless compute from your Databricks App.

## Recipes

### Connect to a shared cluster

#### Dash

```python
import os
from databricks.connect import DatabricksSession

cluster_id = "0709-132523-cnhxf2p6"

spark = DatabricksSession.builder.remote(
    host=os.getenv("DATABRICKS_HOST"),
    cluster_id=cluster_id
).getOrCreate()

query = "SELECT 'hello' AS message"
result = spark.sql(query).toPandas()
print(result)
```

#### Streamlit

```python
import os
import streamlit as st
from databricks.connect import DatabricksSession

cluster_id = st.text_input("Cluster ID:", placeholder="0709-132523-cnhxf2p6")

if cluster_id:
    spark = DatabricksSession.builder.remote(
        host=os.getenv("DATABRICKS_HOST"),
        cluster_id=cluster_id
    ).getOrCreate()

    result = spark.sql("SELECT 'hello' AS message").toPandas()
    st.dataframe(result)
```

#### Reflex

```python
import os
import asyncio
import reflex as rx
from databricks.connect import DatabricksSession

def run_spark_workload(host: str, cluster_id: str):
    spark = DatabricksSession.builder.remote(
        host=host, cluster_id=cluster_id
    ).getOrCreate()
    return spark.sql("SELECT 'hello' AS message").toPandas().values.tolist()

class ConnectClusterState(rx.State):
    cluster_id: str = ""
    result: list = []

    @rx.event(background=True)
    async def connect_and_run(self):
        host = os.getenv("DATABRICKS_HOST")
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(
            None, run_spark_workload, host, self.cluster_id
        )
        async with self:
            self.result = data
```

### Serverless compute

You can also [connect to serverless compute](https://docs.databricks.com/aws/en/compute/serverless/) instead of a shared cluster. Replace the cluster connection with:

```python
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.serverless(True).getOrCreate()
```

## Resources

- [All-purpose compute](https://docs.databricks.com/aws/en/compute/use-compute) or [serverless compute](https://docs.databricks.com/aws/en/compute/serverless/)

## Permissions

The app service principal needs:
- `CAN ATTACH TO` on the cluster

See [Compute permissions](https://docs.databricks.com/aws/en/compute/clusters-manage#compute-permissions).

## Dependencies

```
databricks-connect
pandas
```

Plus your framework package (`dash`, `streamlit`, or `reflex`).

## Common Pitfalls

- Reflex requires `@rx.event(background=True)` and `asyncio.get_running_loop().run_in_executor()` for blocking Spark calls
- `DATABRICKS_HOST` is auto-injected when deployed; set it manually for local development
- Shared clusters must be running; serverless compute starts on demand
