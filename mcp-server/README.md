# Cookbook recipe MCP server

A small [MCP](https://modelcontextprotocol.io/) server for **coding agents**. It exposes Databricks Apps Cookbook **recipes and skills** as tools so an agent can list snippets, permissions, and sample paths without guessing.

This is **not** a copy of the [AI Dev Kit MCP server](https://github.com/databricks-solutions/ai-dev-kit/tree/main/databricks-mcp-server) (SQL, jobs, Unity Catalog, `manage_app`, …). For those workspace tools use [Databricks managed MCP](https://docs.databricks.com/aws/en/agents/mcp-tools/managed-mcp) / Unity Gateway, or the kit server.

Cursor and Claude Code launch examples (from-scratch prompts, pass/fail) live in the [root README](../readme.md#try-it-in-cursor).

## Tools

| Tool | Purpose |
| ---- | ------- |
| `list_cookbook_recipes` | List recipes; optional `framework`: `dash`, `streamlit`, `reflex`, `fastapi` |
| `get_cookbook_recipe` | Snippet, permissions, resources, sample file paths |
| `list_cookbook_skills` | Composition skills (`build-app`, `tables`, …) |
| `get_cookbook_skill` | Full `SKILL.md` body |

## Install (same client paths as AI Dev Kit)

From the cookbook repo root:

```bash
./mcp-server/mcp_install.sh
```

Default registers **all** clients AI Dev Kit supports. Project vs `--global`:

| Client | Project (`--target-dir`, default: this repo) | Global (`-g`) |
| ------ | --------------------------------------------- | ------------- |
| Claude Code | `.mcp.json` | `~/.claude.json` |
| Cursor | `.cursor/mcp.json` | Settings UI (kit does the same) |
| GitHub Copilot | `.vscode/mcp.json` (`servers`) | Settings UI |
| Codex | `.codex/config.toml` | `~/.codex/config.toml` |
| Gemini CLI | `.gemini/settings.json` | `~/.gemini/settings.json` |
| Antigravity | `~/.gemini/antigravity/mcp_config.json` | same |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` | same |
| OpenCode | `opencode.json` | `~/.config/opencode/opencode.json` |
| Kiro | `.kiro/settings/mcp.json` | `~/.kiro/settings/mcp.json` |

The MCP **server name is `cookbook`**, so it can sit next to kit’s `databricks` server. No `DATABRICKS_CONFIG_PROFILE`. The config uses **absolute paths** to this clone’s venv and `run_server.py` — keep the repo on disk.

```bash
./mcp-server/mcp_install.sh --tools claude,cursor
./mcp-server/mcp_install.sh --global --tools claude
./mcp-server/mcp_install.sh --target-dir ~/tmp/cookbook-scratch
./mcp-server/mcp_install.sh --uninstall
```

**Upgrade:** [root README Upgrade](../readme.md#upgrade) (`git pull`, re-run this script, subscribe to Releases). Cursor / Copilot: enable the **cookbook** server in MCP settings if it is off.

`requirements.txt` pins `mcp>=1.9,<2` (FastMCP API). Do not install mcp 2.x.

## Manual config

```json
{
  "mcpServers": {
    "cookbook": {
      "command": "/absolute/path/to/databricks-apps-cookbook/mcp-server/.venv/bin/python",
      "args": ["/absolute/path/to/databricks-apps-cookbook/mcp-server/run_server.py"]
    }
  }
}
```

No Databricks profile is required. The server only reads this repository.

## Tests

```bash
./mcp-server/tests/test_install_paths.sh
```

Uses a temp `$HOME` and project dir (does not rewrite your real Claude/Cursor configs). Checks the root README launch/upgrade strings, catalog, kit-layout MCP + skills install/uninstall, and FastMCP tools if `mcp-server/.venv` exists.
