# 📖 Databricks Apps Cookbook 🍳

Ready-to-use code snippets for building data and AI applications using [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html).

Learn more about the Databricks Apps Cookbook on **[apps-cookbook.dev](https://apps-cookbook.dev/)**.

## What is the Databricks Apps Cookbook?

- **10+ recipes for common Apps use cases** such as reading and writing to and from tables and volumes, invoking traditional ML models and GenAI, or triggering workflows.
- **Try recipes in the Cookbook app** and simply copy a code snippet to build your own.
- **Description of requirements** (permissions, resources, dependencies) for each recipe.
- Deploy to Databricks Apps or run locally.
- Snippets for **Dash, Streamlit, Reflex, and FastAPI** are available.

![Databricks Apps Cookbook](docs/docs/assets/demo.gif)

## Documentation

Find **deployment instructions** and all **code snippets** on [apps-cookbook.dev](https://apps-cookbook.dev/).

## Recipe index by framework

### Where things live

- **Recipe write-ups:** `.mdx` files under [`docs/docs/<framework>/…`](docs/docs/), published at [apps-cookbook.dev](https://apps-cookbook.dev/).
- **Agent skills:** [`databricks-skills/README.md`](databricks-skills/README.md) — all **`SKILL.md`** files live under **`databricks-skills/<section>/…`** (for example **`workflow/build-app`**, **`workflow/productionize-app-dab`**), not under framework folders.
- **Runnable sample apps:** [`dash/APP_DESCRIPTION.md`](dash/APP_DESCRIPTION.md), [`streamlit/APP_DESCRIPTION.md`](streamlit/APP_DESCRIPTION.md), [`reflex/APP_DESCRIPTION.md`](reflex/APP_DESCRIPTION.md), [`fastapi/APP_DESCRIPTION.md`](fastapi/APP_DESCRIPTION.md). Each describes this app’s pages and links back to the [recipe index](#recipe-index-by-framework), docs site, contributing guide, and deploy instructions. FastAPI also has [`fastapi/README.md`](fastapi/README.md) for run commands and endpoints.
- **Paths:** Prefix **Doc path** below with `docs/docs/<framework>/`, then append `.mdx` for the file on disk.

### Shared recipes (Dash, Streamlit, Reflex, FastAPI)

Doc paths are relative to `docs/docs/<framework>/`. When Dash and Streamlit/Reflex use different paths, both appear in the **Doc path** column. FastAPI often uses `building_endpoints/` instead of folders such as `tables/` or `aiml/`.

| Recipe | Doc path | Dash | Streamlit | Reflex | FastAPI |
| ------ | -------- | :--: | :-------: | :----: | :-----: |
| Get current user | `authentication/users_get_current` | ✓ | ✓ | ✓ | — |
| On-behalf-of user (OAuth) | `authentication/users_obo` | — | ✓ | ✓ | — |
| Retrieve secrets | `external_services/secrets_retrieve` (Dash); `authentication/secrets_retrieve` (Streamlit, Reflex) | ✓ | ✓ | ✓ | — |
| External connections | `external_services/external_connections` | ✓ | ✓ | ✓ | — |
| Connect to compute | `compute/compute_connect` | ✓ | ✓ | ✓ | — |
| Read Delta table | `tables/tables_read`; FastAPI: `building_endpoints/tables_read` | ✓ | ✓ | ✓ | ✓ |
| Edit / write Delta table | `tables/tables_edit`; FastAPI: `building_endpoints/tables_insert` | ✓ | ✓ | ✓ | ✓ |
| Read via Lakebase | `tables/lakebase_read` | — | ✓ | — | — |
| OLTP / Postgres (Lakebase client) | `tables/oltp_database` (Dash); `tables/oltp_database_connect` (Reflex) | ✓ | — | ✓ | — |
| Download from volume | `volumes/volumes_download` | ✓ | ✓ | ✓ | — |
| Upload to volume | `volumes/volumes_upload` | ✓ | ✓ | ✓ | — |
| Charts (Plotly) | `visualizations/visualizations_charts` | — | ✓ | — | — |
| Map visualization | `visualizations/visualizations_map` | — | ✓ | — | — |
| Embed AI/BI dashboard | `bi/embed_dashboard` | ✓ | ✓ | ✓ | — |
| Genie API | `bi/genie_api` | ✓ | ✓ | ✓ | — |
| Invoke model serving | `aiml/ml_serving_invoke` | ✓ | ✓ | ✓ | — |
| Vector search | `aiml/ml_vector_search` | ✓ | ✓ | ✓ | — |
| MCP connect | `aiml/mcp_connect`; FastAPI: `building_endpoints/mcp_connect` | ✓ | ✓ | ✓ | ✓ |
| Run workflow (job) | `workflows/workflows_run` | ✓ | ✓ | ✓ | — |
| Get workflow results | `workflows/workflows_get_results` | ✓ | ✓ | ✓ | — |

**Sample code:** [`dash/pages/`](dash/pages/) · [`streamlit/views/`](streamlit/views/) · [`reflex/app/pages/`](reflex/app/pages/) · [`fastapi/routes/`](fastapi/routes/). Reflex page modules are listed in [`reflex/APP_DESCRIPTION.md`](reflex/APP_DESCRIPTION.md).

### FastAPI-only guides

All under `docs/docs/fastapi/`:

| Guide | Doc path |
| ----- | -------- |
| Create FastAPI app | `getting_started/create` |
| Connections overview | `getting_started/connections/index` |
| Connect from app | `getting_started/connections/connect_from_app` |
| Connect from local | `getting_started/connections/connect_from_local` |
| Connect from external client | `getting_started/connections/connect_from_external` |
| Test the app | `getting_started/test` |
| Lakebase connection | `getting_started/lakebase_connection` |
| Lakebase create resources | `building_endpoints/lakebase/lakebase_resources_create` |
| Lakebase delete resources | `building_endpoints/lakebase/lakebase_resources_delete` |
| Lakebase orders API | `building_endpoints/lakebase/lakebase_orders` |
| Stream video from volume | `building_endpoints/volumes_stream_video` |

## Contributions

We welcome contributions! See **[`CONTRIBUTING.md`](CONTRIBUTING.md)** for how to add or port a recipe (code, docs, README index), testing expectations, and the pull request process. Submit a [pull request](https://github.com/databricks-solutions/databricks-apps-cookbook/pulls) or raise an [issue](https://github.com/databricks-solutions/databricks-apps-cookbook/issues) to report a bug or feature request.

Not sure what to contribute? Here are some commonly requested samples:

- Write data from a form into a Delta table
- Display coordinates from a Delta table in a map component
- Display data from a Delta table in Streamlit/Dash-native diagram components
- Gradio implementation
- Flask implementation

## Support

These samples are experimental and meant for demonstration purposes only. They are provided as-is and without formal support by Databricks. Ensure your organization's security, compliance, and operational best practices are applied before deploying them to production.

## License

&copy; 2025 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the [Databricks License](https://databricks.com/db-license-source). All included or referenced third party libraries are subject to the licenses set forth below.

| library   | description                                       | license    | source                                           |
| --------- | ------------------------------------------------- | ---------- | ------------------------------------------------ |
| Plotly    | Graphing library for interactive visualizations   | MIT        | [GitHub](https://github.com/plotly/plotly.py)    |
| Dash      | Framework for building web apps with Plotly       | MIT        | [GitHub](https://github.com/plotly/dash)         |
| Streamlit | App framework for Machine Learning and Data Apps  | Apache 2.0 | [GitHub](https://github.com/streamlit/streamlit) |
| FastAPI   | High-performance API framework based on Starlette | MIT        | [GitHub](https://github.com/tiangolo/fastapi)    |
