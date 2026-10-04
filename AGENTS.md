# Agent instructions

This repository is the **Databricks Apps Cookbook**: tested **Dash, Streamlit, Reflex, and FastAPI** recipes plus composition skills. Follow **[readme.md](readme.md)** — especially **Choose a path** and **Build a Python app with an agent**.

## When to stop

Do **not** use this cookbook if the user wants:

- Charts/KPIs only → [AI/BI (Lakeview) dashboards](https://docs.databricks.com/aws/en/dashboards/)
- Natural-language apps in the Databricks UI / App Spaces → [Genie App Builder](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/genie-app-builder) (AppKit; Beta)
- Default new custom-code app (TypeScript/React) → official **AppKit** via [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) / `databricks aitools install` (`databricks-apps`, `databricks apps init`)
- React + FastAPI toolkit → [apx](https://github.com/databricks-solutions/apx)
- Databricks **workspace tools** for the coding agent (SQL, UC functions, Genie, AI Search) → official [managed MCP](https://docs.databricks.com/aws/en/agents/mcp-tools/managed-mcp) / Unity Gateway (`ug mcp add`), plus AI Dev Kit skills.

Cookbook in-app MCP: [`databricks-skills/aiml`](databricks-skills/aiml/SKILL.md). Recipe MCP for agents: [`mcp-server/`](mcp-server/) (`./mcp-server/mcp_install.sh`). Clone and install from public GitHub (no Databricks-internal npm). Upgrade after a GitHub release: [readme.md § Upgrade](readme.md#upgrade).

## When to use this repo

User asked for **Dash, Streamlit, Reflex, or FastAPI** (or is extending these sample apps).

1. Load [`databricks-skills/build-app/SKILL.md`](databricks-skills/build-app/SKILL.md).
2. Load the matching category skill under [`databricks-skills/`](databricks-skills/) (`tables`, `authentication`, …).
3. Copy from the README [recipe index](readme.md#recipe-index-by-framework) → `docs/docs/<framework>/…` and `dash/`, `streamlit/`, `reflex/`, or `fastapi/`. If the **cookbook MCP** is connected, call `list_cookbook_recipes` / `get_cookbook_recipe` instead of guessing paths. Do not invent code outside those sources.
4. After the app runs, optionally [`databricks-skills/productionize-app-dab/SKILL.md`](databricks-skills/productionize-app-dab/SKILL.md).

Official platform skills (auth scopes, `apps deploy`, AppKit) come from AI Dev Kit / `databricks aitools`. Cookbook skills are recipes only.

## Contributing to this repo

Follow [`CONTRIBUTING.md`](CONTRIBUTING.md) for recipes and [`CLAUDE.md`](CLAUDE.md) for adding skills.
