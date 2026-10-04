---
name: build-app
description: >-
  Build Databricks Apps from this cookbook: minimum folder layout and app.yaml
  per framework (Dash, Streamlit, Reflex, FastAPI), multi-page wiring, docs
  category-first workflow then README recipes, runtime rules, combining recipes.
  Feature code only from repo samples and docs/docs/*.mdx. After the app runs,
  follow [`productionize-app-dab`](../productionize-app-dab/SKILL.md)
  for Databricks Asset Bundles (DABs).
---

# Build a Databricks App

## Constraints (non-negotiable)

Implementations **must** trace to:

| Layer | Source |
| ----- | ------ |
| Samples | [`dash/`](../../../dash/), [`streamlit/`](../../../streamlit/), [`reflex/`](../../../reflex/), [`fastapi/`](../../../fastapi/) |
| Docs | [`docs/docs/`](../../../docs/docs/) → [apps-cookbook.dev](https://apps-cookbook.dev/) |

Those pairs are **tested together**. Do not treat generic tutorials or external snippets as authoritative.

**Outside scope:** React/Vue/Angular SPAs, Gradio-only, Flask-only, etc.—**no tested recipes in this repo.** Point to [Databricks Apps docs](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html).

**FastAPI:** This cookbook ships **API samples + docs**, not a bundled SPA under `/`.

---

## Operating sequence

Order matters—especially **categories before individual recipes**.

1. **Gather constraints** — Audience, browser vs API consumers, maintenance expectations.

2. **Select one primary framework** — Dash, Streamlit, Reflex, or FastAPI using the [recipe index](../../../README.md#recipe-index-by-framework) and **Framework matrix** so planned capabilities have **✓**.

3. **Identify documentation categories first** — Before copying specific `.mdx` files, determine which **`docs/docs/<framework>/<category>/`** folders apply (authentication, tables, workflows, …). Use **Recipe categories** below as the taxonomy: each category groups related permissions, dependencies, and patterns. Skipping this step produces mismatched grants and duplicate connection logic.

4. **Map categories → concrete recipes** — Within each category, pick README rows / **Doc path** stems → specific `.mdx` files + matching sample modules.

5. **Compose** — Follow **Combining recipes**; extend the cookbook only via [`CONTRIBUTING.md`](../../../CONTRIBUTING.md).

6. **Wire `app.yaml` and deploy** — Single process for the whole app (all pages/routes); **`command`** + **`env`** / **`valueFrom`** per **app.yaml** and **Databricks Apps runtime** below; deploy via [`docs/docs/deploy.md`](../../../docs/docs/deploy.md).

---

## Minimum app structure (per framework)

One deployable app = **one** top-level folder with **`app.yaml`** at its root. Multi-page UIs still use **one** `app.yaml`—the runtime serves every page/route from one process.

| Piece | Dash | Streamlit | Reflex | FastAPI |
| ----- | ---- | --------- | ------ | ------- |
| Entry | [`app.py`](../../../dash/app.py) | [`app.py`](../../../streamlit/app.py) | [`reflex/app/app.py`](../../../reflex/app/app.py) (imports app) | [`app.py`](../../../fastapi/app.py) / ASGI `app` |
| Multi-page / routes | [`pages/`](../../../dash/pages/) (`dash.pages`) | [`views/`](../../../streamlit/views/) + [`view_groups.py`](../../../streamlit/view_groups.py) | [`app/pages/`](../../../reflex/app/pages/) + [`cookbook_state.py`](../../../reflex/app/states/cookbook_state.py) nav | [`routes/`](../../../fastapi/routes/) + router include |
| Config / theme | [`assets/`](../../../dash/assets/), styles | [`.streamlit/`](../../../streamlit/.streamlit/) optional | [`theme.py`](../../../reflex/app/theme.py), [`rxconfig.py`](../../../reflex/rxconfig.py) | [`config/`](../../../fastapi/config/) |
| Dependencies | [`requirements.txt`](../../../dash/requirements.txt) | [`requirements.txt`](../../../streamlit/requirements.txt) | [`requirements.txt`](../../../reflex/requirements.txt) | [`requirements.txt`](../../../fastapi/requirements.txt) |
| App metadata | [`APP_DESCRIPTION.md`](../../../dash/APP_DESCRIPTION.md) | [`APP_DESCRIPTION.md`](../../../streamlit/APP_DESCRIPTION.md) | [`APP_DESCRIPTION.md`](../../../reflex/APP_DESCRIPTION.md) | [`README.md`](../../../fastapi/README.md), [`APP_DESCRIPTION.md`](../../../fastapi/APP_DESCRIPTION.md) |
| Bundle / workspace | [`app.yaml`](../../../dash/app.yaml) | [`app.yaml`](../../../streamlit/app.yaml) | [`app.yaml`](../../../reflex/app.yaml), [`databricks.yml`](../../../reflex/databricks.yml) if used | [`app.yaml`](../../../fastapi/app.yaml) |

### Multi-page behavior (same `app.yaml`)

| Framework | How multiple screens work |
| --------- | --------------------------- |
| **Dash** | **`dash.pages`**: one module per screen under **`pages/`**; [`app.py`](../../../dash/app.py) hosts layout + [`sidebar_structure`](../../../dash/app.py) for nav order/labels. |
| **Streamlit** | **`view_groups.py`** defines groups → **`app.py`** builds **`st.navigation`** pages from those definitions → **`views/*.py`** per screen. |
| **Reflex** | **`app/pages/`** components + routes in **`cookbook_state.navigation_items`** (and related collapsed-section state). |
| **FastAPI** | **Routers** (e.g. **`routes/v1/`**) mounted under one **`FastAPI`** app—OpenAPI covers all endpoints at **`/docs`**. |

Adding a recipe usually means **adding one page/view/router module** and **registering it** in the framework’s nav/registry—not a second `app.yaml`.

---

## `app.yaml` (cookbook-aligned)

- **`command`:** must launch the framework entrypoint (see table below). Match the sample folder’s [`app.yaml`](../../../dash/app.yaml) / [`streamlit/app.yaml`](../../../streamlit/app.yaml) / [`reflex/app.yaml`](../../../reflex/app.yaml) / [`fastapi/app.yaml`](../../../fastapi/app.yaml).
- **`env`:** inject resource IDs via **`valueFrom`** keys tied to resources configured on the app in the workspace UI—**never** hardcode warehouse IDs, secret names, or Lakebase identifiers in source ([Databricks Apps resources](https://docs.databricks.com/en/dev-tools/databricks-apps/resources.html)).
- **Ports:** respect **`DATABRICKS_APP_PORT`** (default **8000**); **do not bind 8080**. FastAPI commands should listen on **`0.0.0.0`** and the chosen port (see FastAPI sample).

| Framework | Typical `command` |
| --------- | ----------------- |
| Dash | `["python", "app.py"]` |
| Streamlit | `["streamlit", "run", "app.py"]` |
| Reflex | `["reflex", "run", "--env", "prod"]` |
| FastAPI | `["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]` — align port with runtime |

Multi-page apps do **not** add extra `command` entries—navigation is entirely inside the Python tree above.

---

## Databricks Apps runtime (with cookbook feature code)

Authoritative platform detail: **[Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)**.

### Platform rules

| Rule | Requirement |
| ---- | ----------- |
| Credentials | **`databricks.sdk.core.Config()`** — no hardcoded tokens |
| Resource IDs | **`app.yaml` `env`** + **`valueFrom`** — no literals for warehouses, endpoints, Lakebase, secrets |
| Dash layout | **`dash-bootstrap-components`** / Bootstrap themes |
| Streamlit SQL | **`@st.cache_resource`** for connector-backed resources |
| FastAPI serve | **`uvicorn`** for deployment—not a dev-only server in prod |
| Port | **`DATABRICKS_APP_PORT`** (default **8000**) — **not 8080** |

### Authorization (two layers)

| Model | Mechanism | Typical use |
| ----- | ----------- | ----------- |
| **App (SP)** | `DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET`; **`Config()`** | Shared data, jobs, resources for all users |
| **User (OBO)** | **`x-forwarded-access-token`** when deployed | Per-user UC enforcement |

### App resources (types)

Use managed keys in **`valueFrom`**: SQL warehouse, Lakebase DB, serving endpoint, secrets, UC volumes, vector search, Genie spaces, UC connections/functions, MLflow experiments, Lakeflow jobs—only what your chosen recipes need.

### Data backends

| Backend | When | Cookbook touchpoints |
| ------- | ---- | -------------------- |
| **SQL warehouse** | Analytical Delta SQL | `tables/*`, many `aiml/*`, `bi/*` |
| **Lakebase** | Transactional / low-latency | Lakebase + OLTP recipes; add **`psycopg2`** / **`asyncpg`** to **`requirements.txt`** if used |
| **Databricks SDK** | Jobs, clusters, UC APIs | workflows, compute |

### Runtime snapshot

Python **3.11**, ~**2 vCPU / 6 GB**; frameworks **pre-installed**—only **extra** deps go in **`requirements.txt`**.

---

## Recipe categories (docs “skills” — consult before specific recipes)

Treat each **`docs/docs/<framework>/<category>/`** folder as a **slice** to understand first: shared concerns, permissions, and deps for that domain. **Then** open specific `.mdx` files (README **Doc path** + `.mdx`).

Sample code roots: **`dash/pages/`**, **`streamlit/views/`**, **`reflex/app/pages/`**, **`fastapi/routes/`** (Reflex filenames vary—[`reflex/APP_DESCRIPTION.md`](../../../reflex/APP_DESCRIPTION.md)).

**Dash / Streamlit / Reflex:**

| Category | Covers |
| -------- | ------ |
| **`authentication/`** | Current user; OAuth OBO (Streamlit/Reflex). Secrets: Streamlit/Reflex → `authentication/secrets_retrieve`; Dash → **`external_services/secrets_retrieve`**. |
| **`external_services/`** | External connections; Dash secrets live here. |
| **`compute/`** | Interactive compute attach. |
| **`tables/`** | Delta read/write; Streamlit Lakebase read; OLTP (Dash / Reflex variants). |
| **`volumes/`** | Upload / download. |
| **`visualizations/`** | Charts & maps (Streamlit-only ✓ in README). |
| **`bi/`** | Embedded dashboards; Genie. |
| **`aiml/`** | Serving, vector search, MCP. |
| **`workflows/`** | Run jobs; retrieve results. |

**FastAPI:** [`getting_started/`](../../../docs/docs/fastapi/getting_started/) vs [`building_endpoints/`](../../../docs/docs/fastapi/building_endpoints/) — see README **FastAPI-only** table.

---

## Framework matrix

| Axis | Dash | Streamlit | Reflex | FastAPI |
| ---- | ---- | --------- | ------ | ------- |
| Surface | Python UI | Python UI | Python UI | HTTP API |
| Strength | Plotly / analytics | Defaults / speed | Reactive Python | REST + Lakebase samples |

---

## Architecture checklist

- **Trust boundary:** privileged access only in the **Apps server process**.
- **Permissions:** union of every involved `.mdx` **Permissions** section.
- **Deploy:** [`docs/docs/deploy.md`](../../../docs/docs/deploy.md).

---

## Combining recipes

1. **Decompose** goals → atomic capabilities → README rows / Doc path stems.
2. **Filter** by **✓** for the chosen framework.
3. **Resolve resources once** — shared `Config`, env, helpers.
4. **Union** permissions and **`requirements.txt`**.
5. **Default shape:** **one recipe ≈ one page / view / route group** + nav wiring—see **Multi-page behavior**.
6. **Ordering:** mostly orthogonal; respect prerequisites (e.g. secrets before external connections).

**Chain:** README → `docs/docs/.../*.mdx` → matching sample file(s).

---

## Inputs useful for framework selection

- **Interaction:** Python browser UI vs HTTP API consumers.
- **UI bias:** Streamlit defaults vs Dash visualization vs Reflex.
- **Ownership:** who maintains the deployed app.

Dual stack (UI + FastAPI): two folders, two doc trees—rare.

---

## Follow-up: production bundle (DABs)

When the app **works** from **`dash/`**, **`streamlit/`**, **`reflex/`**, or **`fastapi/`** (correct **`app.yaml`**, recipes composed), use **`productionize-app-dab`** to wrap it in **Databricks Asset Bundles**: **`databricks.yml`**, **`resources/app.yml`**, **`src/app/`** packaging, **`bundle deploy` / `run`**, optional CI/CD—that skill is **framework-specific** (Streamlit vs Dash vs Reflex vs FastAPI **`command`** and folder copy).

→ **[`../productionize-app-dab/SKILL.md`](../productionize-app-dab/SKILL.md)**

---

## Related files

- [`README.md`](../../../README.md) — Recipe index.
- [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) — Porting or adding recipes.
- [`databricks-skills/README.md`](../../README.md) — Skill sections index (all skills live under **`databricks-skills/`**, not under framework folders).
