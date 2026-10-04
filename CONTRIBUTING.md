# Contributing

For humans and coding agents. A **recipe** is documented behavior plus runnable sample code. Mirror an existing recipe in the same category when adding something new.

**Agent skills** belong under **[`databricks-skills/<section>/<skill-name>/`](databricks-skills/README.md)** only—see **[`databricks-skills/README.md`](databricks-skills/README.md)** for sections and naming. Do not add **`SKILL.md`** files under **`dash/`**, **`streamlit/`**, **`reflex/`**, or **`fastapi/`**.

## What to include

For each framework you support:

1. **Sample code** in the app folder for that framework.
2. **Documentation** at `docs/docs/<framework>/…/<slug>.mdx`, using the same sections as sibling pages (code snippet, resources, permissions, dependencies).
3. **[README recipe table](README.md#recipe-index-by-framework)** updated: checkmarks, **Doc path**, and when Dash and Streamlit/Reflex disagree on folder names (for example secrets under `external_services/` versus `authentication/`).
4. **`APP_DESCRIPTION.md`** in each UI sample app you changed, when users see new or renamed pages. For FastAPI, update **`README.md`** or **`APP_DESCRIPTION.md`** when routes or setup change.

Preview documentation locally: `cd docs`, `npm install`, `npm run start`.

A recipe may target only one framework (the README shows — for the others). If you add coverage across frameworks, finish every column you mark with a checkmark.

## Sample code locations

| Framework | Code | Navigation |
|-----------|------|------------|
| Dash | [`dash/pages/`](dash/pages/) | [`dash/app.py`](dash/app.py) `sidebar_structure` |
| Streamlit | [`streamlit/views/`](streamlit/views/) | [`streamlit/view_groups.py`](streamlit/view_groups.py) |
| Reflex | [`reflex/app/pages/`](reflex/app/pages/) | [`reflex/app/states/cookbook_state.py`](reflex/app/states/cookbook_state.py) |
| FastAPI | [`fastapi/routes/`](fastapi/routes/) | [`fastapi/routes/v1/__init__.py`](fastapi/routes/v1/__init__.py) |

Follow patterns in neighboring files. Add new Python packages to that framework’s **`requirements.txt`**. Endpoint-focused FastAPI documentation often lives under `docs/docs/fastapi/building_endpoints/`.

## Testing

Run **locally** every framework you touched ([`docs/docs/deploy.md`](docs/docs/deploy.md), section “Run locally”). Run the recipe **in a Databricks workspace** using the permissions described in your `.mdx` page. If you implemented the same recipe in several frameworks, exercise **each** sample application. Describe testing in your pull request.

## Pull requests

Fork if you cannot push upstream. Create a branch from **`main`**, use small commits with clear messages, then open a pull request against **`main`** with a short description of the change, motivation or context (for example an issue link), what you tested (which frameworks, locally and/or in a workspace), and reply to review feedback.

For large additions or API design, open an [issue](https://github.com/databricks-solutions/databricks-apps-cookbook/issues) before investing in a full implementation.
