# Databricks Skills Contributor Guide

For **building apps** from this cookbook (Dash, Streamlit, Reflex, FastAPI), follow [AGENTS.md](AGENTS.md) and the choose-a-path section in [readme.md](readme.md). This file is how to **add or change skills**.

A **new recipe is not a new skill.** Add sample + docs + the README index ([CONTRIBUTING.md](CONTRIBUTING.md)). Add or edit `databricks-skills/<name>/` only for a **new category** or when agents need new composition notes. Consumers pick up a release via [readme.md § Upgrade](readme.md#upgrade).

This repository packages Databricks Apps skills for both Claude Code and Cursor.

## Repository structure

- `databricks-skills/<skill-name>/SKILL.md`: Source of truth for each skill.
- `.claude-plugin/plugin.json`: Plugin manifest and skill directory references.
- `.claude-plugin/marketplace.json`: Marketplace manifest (must include `owner` and a `plugins` array per Claude Code's marketplace schema) so users can `/plugin marketplace add` this repo directly.
- `.claude-plugin/setup.sh`: Session bootstrap message for Claude Code.
- `hooks/hooks.json`: Runs setup on `SessionStart`.
- `install.sh`: Installs skills for Claude, Cursor, Copilot, Codex, Gemini, Antigravity, Windsurf, OpenCode, and Kiro. Default is **project** (current dir / `--target-dir`); `-g` / `--global` writes `$HOME` paths (same layout as AI Dev Kit). Re-run after `git pull` to upgrade.
- `mcp-server/`: Optional recipe MCP for coding agents (`./mcp-server/mcp_install.sh`). Not Databricks workspace MCP. Docs site (`docs/`): public npm (`docs/.npmrc`); Node.js 20+.

## Conventions

- Keep skill directory names lowercase and use underscores when needed (for example `unity_catalog`).
- Every skill directory must include `SKILL.md` with YAML frontmatter:
  - `name`
  - `description`
- Keep descriptions action-oriented so assistants can pick the right skill.
- Update `databricks-skills/README.md` whenever skills are added or renamed.

## Add a new skill

1. Create a new directory under `databricks-skills/`.
2. Add `SKILL.md` with frontmatter and content.
3. Add the new skill path to `.claude-plugin/plugin.json` in `skills`.
4. Add the skill row to `databricks-skills/README.md`.
5. Run `./install.sh --global --tools claude,cursor` (or `--target-dir` for a project) and verify:
   - Claude skill directory is created under `~/.claude/skills/` (global) or `<project>/.claude/skills/`
   - Cursor skill directory is created under `~/.cursor/skills/` or `<project>/.cursor/skills/` (not flattened `.mdc` rules)
