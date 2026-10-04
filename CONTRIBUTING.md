# Contributing

For humans and coding agents. For when to use this cookbook vs AppKit or Genie App Builder, see **[readme.md](readme.md#choose-a-path)** and **[AGENTS.md](AGENTS.md)**. After a change lands in a **release**, consumers follow **[readme.md § Upgrade](readme.md#upgrade)** (`git pull`, re-run install, or `/plugin marketplace update`).

## Recipes vs skills

A **recipe does not become a skill.** They are different layers:

| Layer | What it is | Where |
| ----- | ---------- | ----- |
| **Recipe** | One tested pattern: sample code + docs (snippet, permissions, resources) | `dash/` / `streamlit/` / `reflex/` / `fastapi/` plus `docs/docs/<framework>/…/<slug>.mdx`, plus the [README recipe index](readme.md#recipe-index-by-framework) |
| **Skill** | Agent composition guide for a **category** (tables, volumes, …) or a workflow (`build-app`, `productionize-app-dab`) | **`databricks-skills/<skill-name>/SKILL.md` only** — never under `dash/`, `streamlit/`, `reflex/`, or `fastapi/` |

| If you add… | You also… | You do **not**… |
| ----------- | --------- | ---------------- |
| A recipe in an **existing** category (for example another tables pattern) | Sample + `.mdx` + README checkmark. After merge, MCP `list_cookbook_recipes` / `get_cookbook_recipe` pick it up from `docs/docs/` on the next `git pull` (no MCP code change). Update the matching category skill **only if** it should mention extra grants, a different sample path, or a FastAPI vs Streamlit split. | Create a new `SKILL.md` per recipe |
| A **new category** (new docs folder that is not one of the existing skills) | New `databricks-skills/<name>/`, plugin path, skills README — see **[CLAUDE.md](CLAUDE.md)** | Leave agents with no category skill |
| Skill-only (`build-app`, `productionize-app-dab`) | Follow **[CLAUDE.md](CLAUDE.md)** | Add a recipe unless there is new sample/docs behavior |

`build-app` and `productionize-app-dab` are workflows, not one recipe. Category skills (`tables`, `authentication`, …) point at many recipes.

## What to include (recipe)

Mirror an existing recipe in the same category.

For each framework you support:

1. **Sample code** in the app folder for that framework.
2. **Documentation** at `docs/docs/<framework>/…/<slug>.mdx`, using the same sections as sibling pages (code snippet, resources, permissions, dependencies).
3. **[README recipe table](readme.md#recipe-index-by-framework)** updated: checkmarks and **Doc path**. If the `.mdx` is not in the same folder for every framework, list each path in that cell and label it (today: secrets are `external_services/` in Dash vs `authentication/` in Streamlit and Reflex; Lakebase OLTP is `tables/oltp_database` in Dash vs `tables/oltp_database_connect` in Reflex). FastAPI endpoint pages usually go under `docs/docs/fastapi/building_endpoints/`.
4. **`APP_DESCRIPTION.md`** in each UI sample app you changed, when users see new or renamed pages. For FastAPI, update **`README.md`** or **`APP_DESCRIPTION.md`** when routes or setup change.
5. Category **skill** touch only when the table above says so. Naming: [`databricks-skills/README.md`](databricks-skills/README.md).

Preview the docs site locally (Node.js 20+, **public** npm — `docs/.npmrc` pins `registry.npmjs.org` so the lockfile works on GitHub Actions and laptops outside Databricks): `cd docs`, `npm install`, `npm run start`.

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

If you changed skills or installers, also run `./mcp-server/tests/test_install_paths.sh`.

## Pull requests

Fork if you cannot push upstream. Create a branch from **`main`**, use small commits with clear messages, then open a pull request against **`main`** with a short description of the change, motivation or context (for example an issue link), what you tested (which frameworks, locally and/or in a workspace), and reply to review feedback.

For large additions or API design, open an [issue](https://github.com/databricks-solutions/databricks-apps-cookbook/issues) before investing in a full implementation.

Maintainers: cut a [GitHub Release](https://github.com/databricks-solutions/databricks-apps-cookbook/releases) so people who [subscribed to Releases](readme.md#subscribe-to-releases) get the next upgrade.
