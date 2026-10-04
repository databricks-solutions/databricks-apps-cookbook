---
sidebar_position: 3
---

# Use with coding agents

This page is for **you** (not for the agent). If you use Cursor, Claude Code, or another coding assistant, you can point it at this cookbook so it copies the snippets on this site instead of inventing Dash, Streamlit, Reflex, or FastAPI code.

The GitHub repository is [databricks-solutions/databricks-apps-cookbook](https://github.com/databricks-solutions/databricks-apps-cookbook). Full flags and client path tables live in that [README](https://github.com/databricks-solutions/databricks-apps-cookbook/blob/main/readme.md#coding-agents-cursor-claude-code-and-others).

:::info When *not* to use this cookbook

| You want | Use instead |
| -------- | ----------- |
| Charts and KPIs only, no custom app | [AI/BI (Lakeview) dashboards](https://docs.databricks.com/aws/en/dashboards/) |
| A natural-language app in the Databricks UI | [Genie App Builder](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/genie-app-builder) |
| A new TypeScript/React Databricks App | Official **AppKit** via [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) (`databricks apps init`) |
| React + FastAPI toolkit | [apx](https://github.com/databricks-solutions/apx) |
| The agent to run SQL, jobs, Unity Catalog, Genie against your workspace | [Managed MCP](https://docs.databricks.com/aws/en/agents/mcp-tools/managed-mcp) / Unity Gateway, plus `databricks aitools install` |

This cookbook is the **Python recipe** layer: Dash, Streamlit, Reflex, and FastAPI only.

:::

## What you install

Two optional pieces, both from a local clone of the cookbook:

1. **Skills** — short guides so the assistant picks tables, volumes, auth, and so on.
2. **Recipe MCP** — tools named `list_cookbook_recipes` and `get_cookbook_recipe` so the assistant can pull a snippet and its permissions even if your app folder is empty.

The MCP server only reads this repository. It is **not** Databricks workspace MCP (no SQL warehouse, no Genie). Keep the clone on disk; client config points at it with absolute paths.

```bash
git clone https://github.com/databricks-solutions/databricks-apps-cookbook.git
cd databricks-apps-cookbook

# This folder only (same idea as AI Dev Kit "project" scope)
./install.sh
./mcp-server/mcp_install.sh

# Every repo on this machine
./install.sh --global
./mcp-server/mcp_install.sh --global
```

Default clients match AI Dev Kit (Claude Code, Cursor, Copilot, Codex, Gemini, and others). For Cursor and Claude Code only:

```bash
./install.sh --tools claude,cursor
./mcp-server/mcp_install.sh --tools claude,cursor
```

**A new app folder** (do not open the cookbook itself if you want a from-scratch test):

```bash
COOKBOOK=/path/to/databricks-apps-cookbook
mkdir -p ~/tmp/cookbook-scratch && cd ~/tmp/cookbook-scratch && git init
"$COOKBOOK/install.sh" --target-dir "$PWD"
"$COOKBOOK/mcp-server/mcp_install.sh" --target-dir "$PWD"
```

Claude Code can install skills as a plugin instead of a copy: in Claude, `/plugin marketplace add databricks-solutions/databricks-apps-cookbook` then `/plugin install databricks-skills@databricks-skills`.

## Try it in Cursor

1. **File → Open Folder** on your app (for a from-scratch test: `~/tmp/cookbook-scratch`).
2. Settings → MCP: turn on the **cookbook** server. Restart Cursor if it is missing. Cursor has no global MCP file (same as AI Dev Kit); the installer writes `.cursor/mcp.json` in the project.
3. Ask something that should use a recipe:

   > Build a Streamlit Databricks App that reads a Unity Catalog table. Use Databricks Apps Cookbook recipes only. Do not invent code.

   You should see `app.yaml`, a Streamlit layout, and table-read code that matches [Read Delta table](/docs/streamlit/tables/tables_read) — not a generic Streamlit tutorial.
4. Ask something that should **not** use this cookbook:

   > I want a TypeScript/React Databricks App.

   The assistant should send you to AppKit / AI Dev Kit, not scaffold Dash or Streamlit from here.

## Try it in Claude Code

```bash
cd ~/tmp/cookbook-scratch && claude
```

Confirm a `cookbook` MCP server, then use the same two prompts as Cursor.

## Upgrade on the next release

Copied skills do **not** update by themselves. The recipe MCP serves whatever is in your clone.

1. Subscribe: on GitHub, **Watch** → **Custom** → **Releases** for [databricks-apps-cookbook](https://github.com/databricks-solutions/databricks-apps-cookbook). Notes: [Releases](https://github.com/databricks-solutions/databricks-apps-cookbook/releases).
2. When a release lands, use the **same flags** as the first install:

```bash
cd /path/to/databricks-apps-cookbook
git fetch --tags
git pull
./install.sh
./mcp-server/mcp_install.sh
```

Claude plugin: `/plugin marketplace update databricks-skills` then `/reload-plugins`.

Official Databricks platform skills (AppKit, jobs, …) stay on `databricks aitools update`. That is a different product.

## Recipes vs skills

You do **not** get a new skill for every snippet on this site.

- A **recipe** is one page here (code, permissions, resources) plus the matching sample in GitHub.
- A **skill** is a category guide (`tables`, `authentication`, …) or a workflow (`build-app`). Adding another tables recipe updates the docs; agents see it through MCP after you `git pull`. A new skill is only needed for a **new category**.

How to contribute a recipe: [CONTRIBUTING.md](https://github.com/databricks-solutions/databricks-apps-cookbook/blob/main/CONTRIBUTING.md).
