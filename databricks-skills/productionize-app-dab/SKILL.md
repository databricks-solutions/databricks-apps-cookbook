---
name: productionize-app-dab
description: >-
  Follow-up to build-app: wrap the chosen cookbook framework (Dash, Streamlit,
  Reflex, FastAPI) in a Databricks Asset Bundle (DAB)—framework-specific src/app
  layout, app.yaml commands, bundle validate/deploy/run, CI/CD secrets. Requires
  a working app from build-app before applying. Self-contained YAML and commands.
---

# Bundle a cookbook app with Databricks Asset Bundles (DAB)

Skill id: **`productionize-app-dab`**.

## Relationship to **build-app**

| Phase | Skill | What it does |
| ----- | ----- | ------------ |
| **1 — Implement** | **`build-app`** ([`../build-app/SKILL.md`](../build-app/SKILL.md)) | Choose **Dash / Streamlit / Reflex / FastAPI**, map README recipes to **`docs/docs/`** + sample code, ship **`app.yaml`** for local/workspace run. |
| **2 — Bundle (DAB)** | **`productionize-app-dab`** (this file) | Keep the same framework choice; **package** that app under **`src/app/`** and add **`databricks.yml`** + **`resources/`** so **`databricks bundle deploy`** owns lifecycle and environments. |

Do **not** productionize until the app **runs** from the cookbook folder (or equivalent). Switching framework after bundling means redoing **`src/app`** contents and **`app.yaml` `command`**.

**Pattern origin:** Minimal layout matches the public **`pbv0/databricks-apps-dabs`** reference (bundle root, `resources/app.yml`, `src/app`, optional job + CI)—embedded here without requiring downloads.

---

## Outcomes (all frameworks)

- **`resources/app.yml`** declares an **`apps`** resource with **`source_code_path: ../src/app`**.
- **`databricks.yml`** defines **`targets`** (e.g. `dev` / `prod`) and **`workspace.host`** per environment.
- **`databricks bundle validate` → `deploy` → `run <app-key>`** against the chosen target.
- Optional **GitHub Actions** with **`DATABRICKS_HOST`**, **`DATABRICKS_CLIENT_ID`**, **`DATABRICKS_CLIENT_SECRET`**.

---

## Prerequisites

- **Python** 3.11+, **Databricks CLI** 0.18.0+, workspace with **Apps** enabled.
- Completed **build-app** trajectory: one primary framework and working **`app.yaml`** from the matching cookbook sample.

---

## Shared bundle layout (any framework)

```
project-root/
├── databricks.yml
├── resources/
│   ├── app.yml
│   └── job.yml              # optional
├── src/
│   ├── app/                 # packaged cookbook app (structure varies by framework ↓)
│   └── job/                 # optional bundle job code
└── README.md
```

**`databricks.yml`** (same idea for every framework—adjust **`bundle.name`** and app key **`my-app`**):

```yaml
bundle:
  name: my-databricks-app

include:
  - resources/*.yml

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://YOUR-DEV-WORKSPACE.cloud.databricks.com/
    resources:
      apps:
        my-app:
          name: "my-app-dev"

  prod:
    mode: production
    workspace:
      host: https://YOUR-PROD-WORKSPACE.cloud.databricks.com/
    root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}
    permissions:
      - user_name: ${workspace.current_user.userName}
        level: CAN_MANAGE
```

**`resources/app.yml`** (minimal—the **`resources.apps.<key>`** must match **`databricks bundle run <key>`**):

```yaml
resources:
  apps:
    my-app:
      name: "my-app"
      source_code_path: ../src/app
      description: "Databricks App deployed via Asset Bundle."
```

Optional **job-linked app** and **`resources/job.yml`** blocks are identical across frameworks—see end of this file.

---

## Framework-specific: what goes into **`src/app/`**

Copy from the cookbook folder **`dash/`**, **`streamlit/`**, **`reflex/`**, or **`fastapi/`** into **`src/app/`**, **preserving relative paths** so imports and framework conventions still work.

| Framework | Copy from repo folder | Must exist under **`src/app/`** | **`app.yaml` `command`** (production-shaped) |
| --------- | ---------------------- | --------------------------------- | --------------------------------------------- |
| **Streamlit** | **`streamlit/`** | **`app.py`**, **`view_groups.py`**, **`views/`**, **`assets/`**, **`requirements.txt`**, **`.streamlit/`** if used | `["streamlit", "run", "app.py"]` |
| **Dash** | **`dash/`** | **`app.py`**, **`pages/`**, **`assets/`**, **`requirements.txt`** | `["python", "app.py"]` |
| **Reflex** | **`reflex/`** | Whole tree: **`rxconfig.py`**, **`app/`** (pages, states, …), **`requirements.txt`**, **`app.yaml`** already at reflex root in cookbook—place those files so **`reflex run`** resolves (same layout as sample; **`src/app`** = reflex project root) | `["reflex", "run", "--env", "prod"]` |
| **FastAPI** | **`fastapi/`** | **`app.py`** (ASGI **`app`**), **`routes/`**, **`config/`**, **`requirements.txt`**, tests optional | `["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]` |

### Streamlit

- Single process: **`app.py`** drives **`st.navigation`**; do **not** split **`command`** per view.
- **`app.yaml`** example:

```yaml
command:
  - "streamlit"
  - "run"
  - "app.py"
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

### Dash

- **`dash.pages`** loads **`pages/`** automatically; **`app.py`** hosts sidebar—one **`command`** only.
- **`app.yaml`** example:

```yaml
command:
  - "python"
  - "app.py"
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

### Reflex

- Treat **`src/app/`** as the **Reflex project root** (mirror **`reflex/`** in the cookbook: **`rxconfig.py`** beside **`app/`** package).
- **`reflex run --env prod`** expects that layout; **`CI`** or env flags may appear in sample **`app.yaml`**—merge with workspace **`valueFrom`** as needed.
- **`app.yaml`** example:

```yaml
command:
  - "reflex"
  - "run"
  - "--env"
  - "prod"
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

### FastAPI

- **Headless API**: no multi-page UI—**`command`** starts **uvicorn** only; routes live under **`routes/`** inside **`src/app/`**.
- Bind **`0.0.0.0`** and align port with **`DATABRICKS_APP_PORT`** / bundle expectations (default **8000**).
- **`app.yaml`** example:

```yaml
command:
  - "uvicorn"
  - "app:app"
  - "--host"
  - "0.0.0.0"
  - "--port"
  - "8000"
env:
  - name: DATABRICKS_WAREHOUSE_ID
    valueFrom: sql_warehouse
```

- Ensure **`PYTHONPATH`** / imports match **`app:app`** (module **`app`** with attribute **`app`**), same as cookbook **`fastapi/`** layout.

---

## Commands (same for all frameworks)

```bash
databricks auth login --host https://YOUR-WORKSPACE.cloud.databricks.com/

databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run my-app -t dev
```

Replace **`my-app`** with your **`resources.apps`** key. Use **`-t prod`** when the prod target is configured.

---

## GitHub Actions (conceptual)

| Secret | Purpose |
| ------ | ------- |
| `DATABRICKS_HOST` | Workspace URL |
| `DATABRICKS_CLIENT_ID` | Service principal client ID |
| `DATABRICKS_CLIENT_SECRET` | Service principal secret |

Steps: checkout → install **Databricks CLI** → export secrets for OAuth M2M → **`databricks bundle deploy -t prod`**. Gate **`prod`** on protected branches or releases.

---

## Optional: bundle job + app attachment

**`resources/job.yml`:**

```yaml
resources:
  jobs:
    hello_world:
      name: Serverless Hello World job
      tasks:
        - task_key: task
          spark_python_task:
            python_file: ../src/job/main.py
            environment_key: default
      environments:
        - environment_key: default
          spec:
            client: "1"
```

**`resources/app.yml`** fragment (job must exist):

```yaml
resources:
  apps:
    hello-world-app:
      name: "hello-world-app"
      source_code_path: ../src/app
      resources:
        - name: "app-job"
          job:
            id: ${resources.jobs.hello_world.id}
          permission: "CAN_MANAGE_RUN"
```

---

## Migration checklist (from **build-app**)

1. Confirm **`build-app`** framework and runnable **`app.yaml`** in the cookbook folder.
2. Create **`src/app/`** and copy **that framework’s** tree (table above).
3. Paste the matching **`app.yaml` `command`** block + **`env`** / **`valueFrom`** for **Streamlit / Dash / Reflex / FastAPI**.
4. Add **`databricks.yml`** + **`resources/app.yml`**; **`source_code_path: ../src/app`**.
5. **`databricks bundle validate`** → **`deploy`** → **`bundle run`**.

---

## Pitfalls

- **`source_code_path`** is relative to **`resources/app.yml`**.
- **`valueFrom`** names must match resources attached in bundle **and** workspace configuration.
- **Reflex:** broken **`rxconfig.py` / `app/`** layout is the most common bundle failure—mirror the cookbook **`reflex/`** tree exactly under **`src/app/`**.
- **FastAPI:** wrong **`uvicorn`** module path (`app:app`) breaks deploy—match **`fastapi/app.py`** export.
- **Lakebase / extra wheels:** list in **`src/app/requirements.txt`** if not on the Apps image.

---

## Related files

- [`build-app`](../build-app/SKILL.md) — prerequisite: runnable cookbook app + **`app.yaml`**.
- [`databricks-skills/README.md`](../../README.md) — Skill sections index (all skills under **`databricks-skills/`**, not framework folders).

---

## Relation to the cookbook repo

Productionizing **packages** one cookbook framework directory into **`src/app/`** and adds bundle metadata at repo root. It does **not** replace **`dash/`**, **`streamlit/`**, **`reflex/`**, **`fastapi/`** in the cookbook—those remain source-of-truth samples. Feature and doc changes still follow **`README`** and **`CONTRIBUTING`**.
