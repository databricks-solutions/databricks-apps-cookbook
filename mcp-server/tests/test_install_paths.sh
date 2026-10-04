#!/usr/bin/env bash
# Isolated tests for MCP + skills install paths (AI Dev Kit layout) and catalog.
# Does not write to the real $HOME.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MCP_INSTALL="${ROOT}/mcp-server/mcp_install.sh"
SKILLS_INSTALL="${ROOT}/install.sh"
README="${ROOT}/readme.md"
FAIL=0

assert_file() {
  local path="$1"
  if [[ ! -f "${path}" ]]; then
    echo "FAIL missing ${path}" >&2
    FAIL=1
  fi
}

assert_dir() {
  local path="$1"
  if [[ ! -d "${path}" ]]; then
    echo "FAIL missing dir ${path}" >&2
    FAIL=1
  fi
}

assert_contains() {
  local path="$1"
  local needle="$2"
  if ! grep -qF -- "${needle}" "${path}"; then
    echo "FAIL ${path} missing ${needle}" >&2
    FAIL=1
  fi
}

assert_absent() {
  local path="$1"
  local needle="$2"
  if grep -qF -- "${needle}" "${path}"; then
    echo "FAIL ${path} still has ${needle}" >&2
    FAIL=1
  fi
}

assert_missing() {
  local path="$1"
  if [[ -e "${path}" ]]; then
    echo "FAIL unexpected ${path}" >&2
    FAIL=1
  fi
}

WORKDIR="$(mktemp -d)"
trap 'rm -rf "${WORKDIR}"' EXIT
export HOME="${WORKDIR}/home"
mkdir -p "${HOME}" "${WORKDIR}/proj"

echo "== readme (install, upgrade, Cursor/Claude launch) =="
assert_contains "${README}" "./install.sh --global"
assert_contains "${README}" "./mcp-server/mcp_install.sh --global"
assert_contains "${README}" "--target-dir"
assert_contains "${README}" "git pull"
assert_contains "${README}" "## Upgrade"
assert_contains "${README}" "Watch"
assert_contains "${README}" "github.com/databricks-solutions/databricks-apps-cookbook/releases"
assert_contains "${README}" "Build a Streamlit Databricks App that reads a Unity Catalog table"
assert_contains "${README}" "TypeScript/React Databricks App"
assert_contains "${README}" "list_cookbook_recipes"
assert_contains "${README}" "File → Open Folder"
assert_contains "${README}" "cd ~/tmp/cookbook-scratch && claude"

echo "== docs coding-agents page =="
assert_contains "${ROOT}/docs/docs/coding-agents.md" "Use with coding agents"
assert_contains "${ROOT}/docs/docs/coding-agents.md" "File → Open Folder"
assert_contains "${ROOT}/docs/docs/coding-agents.md" "Watch"
assert_contains "${ROOT}/CONTRIBUTING.md" "recipe does not become a skill"
assert_contains "${ROOT}/CONTRIBUTING.md" "databricks-skills/"

echo "== catalog =="
PYTHONPATH="${ROOT}/mcp-server" python3 - <<'PY'
from catalog import FRAMEWORKS, get_recipe, get_skill, list_recipes, list_skills
recipes = list_recipes()
assert {r["framework"] for r in recipes} == set(FRAMEWORKS)
assert get_recipe("streamlit", "tables_read")["snippet"]
assert "When not to use this skill" in get_skill("build-app")["body"]
print(len(recipes), "recipes", len(list_skills()), "skills")
PY

echo "== MCP project-scope (kit client files) =="
"${MCP_INSTALL}" --skip-venv --target-dir "${WORKDIR}/proj" >/dev/null

assert_file "${WORKDIR}/proj/.mcp.json"
assert_contains "${WORKDIR}/proj/.mcp.json" '"cookbook"'
assert_contains "${WORKDIR}/proj/.mcp.json" "defer_loading"
assert_file "${WORKDIR}/proj/.cursor/mcp.json"
assert_contains "${WORKDIR}/proj/.cursor/mcp.json" '"cookbook"'
assert_file "${WORKDIR}/proj/.vscode/mcp.json"
assert_contains "${WORKDIR}/proj/.vscode/mcp.json" '"servers"'
assert_file "${WORKDIR}/proj/.codex/config.toml"
assert_contains "${WORKDIR}/proj/.codex/config.toml" "[mcp_servers.cookbook]"
assert_file "${WORKDIR}/proj/.gemini/settings.json"
assert_file "${WORKDIR}/proj/opencode.json"
assert_contains "${WORKDIR}/proj/opencode.json" '"type": "local"'
assert_file "${WORKDIR}/proj/.kiro/settings/mcp.json"

echo "== MCP merge preserves other servers =="
python3 - "${WORKDIR}/proj/.mcp.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
cfg = json.loads(p.read_text())
cfg["mcpServers"]["other"] = {"command": "echo"}
p.write_text(json.dumps(cfg))
PY
"${MCP_INSTALL}" --skip-venv --target-dir "${WORKDIR}/proj" --tools claude >/dev/null
assert_contains "${WORKDIR}/proj/.mcp.json" '"other"'
assert_contains "${WORKDIR}/proj/.mcp.json" '"cookbook"'

echo "== MCP uninstall cookbook only =="
"${MCP_INSTALL}" --skip-venv --target-dir "${WORKDIR}/proj" --tools claude --uninstall >/dev/null
assert_absent "${WORKDIR}/proj/.mcp.json" '"cookbook"'
assert_contains "${WORKDIR}/proj/.mcp.json" '"other"'

echo "== MCP global-scope (kit home paths) =="
"${MCP_INSTALL}" --skip-venv --global \
  --tools claude,codex,gemini,antigravity,windsurf,opencode,kiro >/dev/null
assert_file "${HOME}/.claude.json"
assert_contains "${HOME}/.claude.json" '"cookbook"'
assert_file "${HOME}/.codex/config.toml"
assert_file "${HOME}/.gemini/settings.json"
assert_file "${HOME}/.gemini/antigravity/mcp_config.json"
assert_file "${HOME}/.codeium/windsurf/mcp_config.json"
assert_file "${HOME}/.config/opencode/opencode.json"
assert_file "${HOME}/.kiro/settings/mcp.json"

echo "== skills project-scope (kit .claude/skills + .cursor/skills) =="
"${SKILLS_INSTALL}" --target-dir "${WORKDIR}/proj" --tools claude,cursor >/dev/null
assert_file "${WORKDIR}/proj/.claude/skills/build-app/SKILL.md"
assert_file "${WORKDIR}/proj/.cursor/skills/build-app/SKILL.md"
assert_file "${WORKDIR}/proj/.cursor/skills/tables/SKILL.md"
assert_missing "${WORKDIR}/proj/.cursor/rules/build-app.mdc"

echo "== skills global-scope =="
"${SKILLS_INSTALL}" --global --tools claude,cursor >/dev/null
assert_file "${HOME}/.claude/skills/build-app/SKILL.md"
assert_file "${HOME}/.cursor/skills/tables/SKILL.md"

echo "== skills upgrade overwrites =="
echo "stale" > "${HOME}/.claude/skills/build-app/SKILL.md"
"${SKILLS_INSTALL}" --global --tools claude >/dev/null
assert_contains "${HOME}/.claude/skills/build-app/SKILL.md" "When not to use this skill"

echo "== skills uninstall cookbook only =="
mkdir -p "${HOME}/.claude/skills/unrelated"
echo keep > "${HOME}/.claude/skills/unrelated/SKILL.md"
"${SKILLS_INSTALL}" --global --tools claude --uninstall >/dev/null
assert_missing "${HOME}/.claude/skills/build-app"
assert_file "${HOME}/.claude/skills/unrelated/SKILL.md"

echo "== skills extra clients (project) =="
"${SKILLS_INSTALL}" --target-dir "${WORKDIR}/proj" --tools copilot,codex,gemini >/dev/null
assert_file "${WORKDIR}/proj/.github/skills/build-app/SKILL.md"
assert_file "${WORKDIR}/proj/.agents/skills/build-app/SKILL.md"
assert_file "${WORKDIR}/proj/.gemini/skills/build-app/SKILL.md"

if [[ -x "${ROOT}/mcp-server/.venv/bin/python" ]]; then
  echo "== FastMCP tools =="
  cd "${ROOT}/mcp-server"
  .venv/bin/python - <<'PY'
from server import get_cookbook_recipe, list_cookbook_recipes, list_cookbook_skills
assert list_cookbook_recipes("reflex")["count"] > 0
assert get_cookbook_recipe("dash", "mcp_connect")["snippet"]
assert list_cookbook_skills()["count"] == 12
print("FastMCP ok")
PY
fi

if [[ "${FAIL}" -ne 0 ]]; then
  echo "FAILED"
  exit 1
fi
echo "ALL PASSED"
