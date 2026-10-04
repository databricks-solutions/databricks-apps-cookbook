# Databricks Apps Skills

AI coding assistant skills for composing **Dash, Streamlit, FastAPI, and Reflex** apps from this cookbook. Works with **Cursor**, **Claude Code**, and the other clients listed in the [root README](../readme.md#coding-agents-cursor-claude-code-and-others).

These skills are **recipe composition**, not a replacement for official Databricks AI Tools. For AppKit, platform auth/deploy, jobs, pipelines, and **workspace MCP** (SQL, UC, Genie), install [AI Dev Kit](https://github.com/databricks-solutions/ai-dev-kit) / `databricks aitools install` and [managed MCP](https://docs.databricks.com/aws/en/agents/mcp-tools/managed-mcp). For natural-language apps in the Databricks UI, use [Genie App Builder](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/genie-app-builder). In-app **MCP connect** (`aiml`) is the app calling an MCP server. To let the coding agent **query this cookbook**, run [`../mcp-server/mcp_install.sh`](../mcp-server/mcp_install.sh). When this repo is the right path, start with [`build-app`](build-app/SKILL.md) — see the [root README](../readme.md#choose-a-path).

Each skill covers one aspect of cookbook Apps development — authentication, table access, volume operations, and more — with framework-specific guidance for Dash, Streamlit, FastAPI, and Reflex.

## Available Skills

| Skill | Description |
|-------|-------------|
| `authentication` | OAuth (user + app auth), token management, retrieving current user |
| `tables` | Read/write Delta tables, Lakebase connectivity, table editing |
| `unity_catalog` | Browse catalogs and schemas in Unity Catalog |
| `volumes` | Upload/download files from Unity Catalog Volumes |
| `visualizations` | Build chart and map visualizations from table data |
| `aiml` | Invoke ML models, vector search, MCP connections |
| `bi` | Embed AI/BI dashboards, Genie API integration |
| `compute` | Connect to SQL warehouses and clusters |
| `external_services` | External connections and third-party service integration |
| `workflows` | Trigger and monitor Databricks Jobs |
| `build-app` | Scaffold a Databricks App from the cookbook (Dash, Streamlit, Reflex, FastAPI) |
| `productionize-app-dab` | Wrap a cookbook app in a Databricks Asset Bundle (DAB) |

## Installation

**Project vs `--global`, upgrade, and Cursor/Claude launch examples** are in the [root README](../readme.md#coding-agents-cursor-claude-code-and-others).

```bash
# From the cookbook clone (project = this folder)
./install.sh
./mcp-server/mcp_install.sh

# All repos on this machine
./install.sh --global
./mcp-server/mcp_install.sh --global
```

`./install.sh` copies `databricks-skills/<name>/` into the same skill directories AI Dev Kit uses:

| Client | Project (default / `--target-dir`) | Global (`-g`) |
| ------ | ---------------------------------- | ------------- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot | `.github/skills/` | `~/.github/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Gemini CLI | `.gemini/skills/` | `~/.gemini/skills/` |
| Antigravity | `.agents/skills/` | `~/.gemini/antigravity/skills/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` |
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` |
| Kiro | `.kiro/skills/` | `~/.kiro/skills/` |

**Upgrade:** see the [root README Upgrade](../readme.md#upgrade) section (`git pull` + re-run install, or `/plugin marketplace update`). Subscribe to [GitHub Releases](https://github.com/databricks-solutions/databricks-apps-cookbook/releases) via **Watch → Custom → Releases**.

### Claude Code plugin marketplace

Add this repo as a marketplace so skills stay in the plugin instead of a copied folder.

**From GitHub:**

```text
/plugin marketplace add databricks-solutions/databricks-apps-cookbook
/plugin install databricks-skills@databricks-skills
/reload-plugins
```

**From a local clone:**

```text
/plugin marketplace add /absolute/path/to/databricks-apps-cookbook
/plugin install databricks-skills@databricks-skills
/reload-plugins
```

After install, skills appear under the `databricks-skills:` namespace. Manage with:

- `/plugin list`
- `/plugin marketplace update databricks-skills` — pull the next release
- `/plugin uninstall databricks-skills@databricks-skills`

## Usage

Once installed, the skills activate automatically when your AI assistant detects a relevant task. For example:

- Ask *"Set up OAuth for my Streamlit app"* and the `authentication` skill kicks in
- Ask *"Read data from a Delta table in Dash"* and the `tables` skill provides the right pattern
- Ask *"Add file upload to my FastAPI app"* and the `volumes` skill guides the implementation

No special commands needed — just describe what you want to build.

## Skill Format

Each skill is a directory containing a `SKILL.md` file:

```
authentication/
├── SKILL.md          # Main instructions (required)
├── reference.md      # Detailed docs (optional)
└── examples/         # Code examples (optional)
```

The `SKILL.md` format is compatible with both Cursor and Claude Code.
