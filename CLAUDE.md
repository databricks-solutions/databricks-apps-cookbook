# Databricks Skills Contributor Guide

This repository packages Databricks Apps skills for both Claude Code and Cursor.

## Repository structure

- `databricks-skills/<skill-name>/SKILL.md`: Source of truth for each skill.
- `.claude-plugin/plugin.json`: Plugin manifest and skill directory references.
- `.claude-plugin/marketplace.json`: Marketplace manifest (must include `owner` and a `plugins` array per Claude Code's marketplace schema) so users can `/plugin marketplace add` this repo directly.
- `.claude-plugin/setup.sh`: Session bootstrap message for Claude Code.
- `hooks/hooks.json`: Runs setup on `SessionStart`.
- `install.sh`: Installs skills for `claude`, `cursor`, or `all`.

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
5. Run `./install.sh all` and verify:
   - Claude skill directory is created under `~/.claude/skills/`
   - Cursor rule file is created under `~/.cursor/rules/`
