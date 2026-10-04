#!/usr/bin/env bash
# Register the cookbook recipe MCP server using the same client config paths as
# AI Dev Kit's databricks-mcp-server/mcp_install.sh. Server name is "cookbook"
# so it can sit next to the kit's "databricks" server.
#
# Local recipes/skills only — no Databricks profile / workspace tools.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MCP_ENTRY="${SCRIPT_DIR}/run_server.py"
VENV_DIR="${SCRIPT_DIR}/.venv"
SERVER_NAME="cookbook"
JSON_PYTHON="python3"

DEFAULT_TOOLS="claude,cursor,copilot,codex,gemini,antigravity,windsurf,opencode,kiro"
TOOLS="${DEFAULT_TOOLS}"
SCOPE="project"
TARGET_DIR="${REPO_ROOT}"
UNINSTALL=false
DRY_RUN=false
SKIP_VENV=false

usage() {
  cat <<'EOF'
Usage: ./mcp-server/mcp_install.sh [options]

  --tools LIST     claude,cursor,copilot,codex,gemini,antigravity,windsurf,opencode,kiro
                   (default: all of the above)
  -g, --global     Write home-dir configs (same layout as AI Dev Kit)
  --target-dir DIR Project-scope root (default: cookbook repo root)
  --skip-venv      Do not create/install mcp-server/.venv
  --uninstall      Remove the "cookbook" MCP entry only
  --dry-run        Print target paths and exit
  -h, --help

Config paths match AI Dev Kit (project vs global). This server does not set
DATABRICKS_CONFIG_PROFILE.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tools) TOOLS="$2"; shift 2 ;;
    -g|--global) SCOPE="global"; shift ;;
    --target-dir) TARGET_DIR="$2"; shift 2 ;;
    --skip-venv) SKIP_VENV=true; shift ;;
    --uninstall) UNINSTALL=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"
VENV_PYTHON="${VENV_DIR}/bin/python"
if [[ "$(uname -s)" == "MINGW"* || "$(uname -s)" == "MSYS"* || "$(uname -s)" == "CYGWIN"* ]]; then
  VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"
fi
if [[ "${SKIP_VENV}" == true && ! -x "${VENV_PYTHON}" ]]; then
  VENV_PYTHON="$(command -v python3)"
fi

echo "Cookbook MCP (recipes + skills)"
echo "  repo:   ${REPO_ROOT}"
echo "  entry:  ${MCP_ENTRY}"
echo "  scope:  ${SCOPE}"
echo "  target: ${TARGET_DIR}"
echo "  tools:  ${TOOLS}"

merge_json() {
  local path="$1"
  local root_key="$2"
  local defer="$3"
  mkdir -p "$(dirname "${path}")"
  if [[ -f "${path}" ]]; then
    cp "${path}" "${path}.bak"
  fi
  "${JSON_PYTHON}" - "${path}" "${root_key}" "${SERVER_NAME}" "${VENV_PYTHON}" "${MCP_ENTRY}" "${defer}" <<'PY'
import json
import sys
from pathlib import Path

path, root_key, name, command, entry, defer = sys.argv[1:7]
p = Path(path)
try:
    cfg = json.loads(p.read_text()) if p.exists() else {}
except json.JSONDecodeError:
    cfg = {}
if not isinstance(cfg, dict):
    cfg = {}
entry_obj = {"command": command, "args": [entry]}
if defer == "true":
    entry_obj["defer_loading"] = True
cfg.setdefault(root_key, {})[name] = entry_obj
p.write_text(json.dumps(cfg, indent=2) + "\n")
PY
}

remove_json() {
  local path="$1"
  local root_key="$2"
  [[ -f "${path}" ]] || return 0
  cp "${path}" "${path}.bak"
  "${JSON_PYTHON}" - "${path}" "${root_key}" "${SERVER_NAME}" <<'PY'
import json
import sys
from pathlib import Path

path, root_key, name = sys.argv[1:4]
p = Path(path)
cfg = json.loads(p.read_text())
servers = cfg.get(root_key, {})
if isinstance(servers, dict):
    servers.pop(name, None)
    if servers:
        cfg[root_key] = servers
    else:
        cfg.pop(root_key, None)
p.write_text(json.dumps(cfg, indent=2) + "\n")
PY
}

merge_toml() {
  local path="$1"
  mkdir -p "$(dirname "${path}")"
  if [[ -f "${path}" ]] && grep -qE "^\[mcp_servers\.${SERVER_NAME}(\.|])" "${path}"; then
    return 0
  fi
  if [[ -f "${path}" ]]; then
    cp "${path}" "${path}.bak"
  fi
  mkdir -p "$(dirname "${path}")"
  cat >> "${path}" <<EOF

[mcp_servers.${SERVER_NAME}]
command = "${VENV_PYTHON}"
args = ["${MCP_ENTRY}"]
EOF
}

remove_toml() {
  local path="$1"
  [[ -f "${path}" ]] || return 0
  grep -qE "^\[mcp_servers\.${SERVER_NAME}(\.|])" "${path}" || return 0
  cp "${path}" "${path}.bak"
  awk -v name="${SERVER_NAME}" '
    $0 ~ "^\\[mcp_servers\\." name "(\\.|])" { skip=1; next }
    /^\[/ { skip=0 }
    !skip { print }
  ' "${path}.bak" > "${path}"
}

merge_opencode() {
  local path="$1"
  mkdir -p "$(dirname "${path}")"
  if [[ -f "${path}" ]]; then
    cp "${path}" "${path}.bak"
  fi
  "${JSON_PYTHON}" - "${path}" "${SERVER_NAME}" "${VENV_PYTHON}" "${MCP_ENTRY}" <<'PY'
import json
import sys
from pathlib import Path

path, name, command, entry = sys.argv[1:5]
p = Path(path)
try:
    cfg = json.loads(p.read_text()) if p.exists() else {}
except json.JSONDecodeError:
    cfg = {}
if not isinstance(cfg, dict):
    cfg = {}
cfg.setdefault("mcp", {})[name] = {
    "type": "local",
    "command": [command, entry],
    "enabled": True,
}
p.write_text(json.dumps(cfg, indent=2) + "\n")
PY
}

remove_opencode() {
  local path="$1"
  [[ -f "${path}" ]] || return 0
  cp "${path}" "${path}.bak"
  "${JSON_PYTHON}" - "${path}" "${SERVER_NAME}" <<'PY'
import json
import sys
from pathlib import Path

path, name = sys.argv[1:3]
p = Path(path)
cfg = json.loads(p.read_text())
mcp = cfg.get("mcp", {})
if isinstance(mcp, dict):
    mcp.pop(name, None)
    if mcp:
        cfg["mcp"] = mcp
    else:
        cfg.pop("mcp", None)
p.write_text(json.dumps(cfg, indent=2) + "\n")
PY
}

# Same layout as AI Dev Kit mcp_install.sh (kit server name is "databricks").
config_for_tool() {
  local tool="$1"
  case "${tool}" in
    claude)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.claude.json|json:mcpServers|defer"
      else
        echo "${TARGET_DIR}/.mcp.json|json:mcpServers|defer"
      fi
      ;;
    cursor)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "MANUAL|cursor-global"
      else
        echo "${TARGET_DIR}/.cursor/mcp.json|json:mcpServers|"
      fi
      ;;
    copilot)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "MANUAL|copilot-global"
      else
        echo "${TARGET_DIR}/.vscode/mcp.json|json:servers|"
      fi
      ;;
    codex)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.codex/config.toml|toml|"
      else
        echo "${TARGET_DIR}/.codex/config.toml|toml|"
      fi
      ;;
    gemini)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.gemini/settings.json|json:mcpServers|"
      else
        echo "${TARGET_DIR}/.gemini/settings.json|json:mcpServers|"
      fi
      ;;
    antigravity)
      echo "${HOME}/.gemini/antigravity/mcp_config.json|json:mcpServers|"
      ;;
    windsurf)
      echo "${HOME}/.codeium/windsurf/mcp_config.json|json:mcpServers|defer"
      ;;
    opencode)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.config/opencode/opencode.json|opencode|"
      else
        echo "${TARGET_DIR}/opencode.json|opencode|"
      fi
      ;;
    kiro)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.kiro/settings/mcp.json|json:mcpServers|defer"
      else
        echo "${TARGET_DIR}/.kiro/settings/mcp.json|json:mcpServers|defer"
      fi
      ;;
    *)
      echo "Unknown tool: ${tool}" >&2
      exit 1
      ;;
  esac
}

apply_spec() {
  local spec="$1"
  local mode="$2"
  IFS='|' read -r path kind extra <<< "${spec}"
  if [[ "${path}" == "MANUAL" ]]; then
    echo " - ${kind}: configure MCP in the client UI (same as AI Dev Kit)"
    return 0
  fi
  if [[ "${DRY_RUN}" == true ]]; then
    echo " - ${mode}: ${path} (${kind})"
    return 0
  fi
  case "${kind}" in
    json:mcpServers)
      if [[ "${mode}" == "remove" ]]; then
        remove_json "${path}" mcpServers
      else
        local defer="false"
        [[ "${extra}" == "defer" ]] && defer="true"
        merge_json "${path}" mcpServers "${defer}"
      fi
      ;;
    json:servers)
      if [[ "${mode}" == "remove" ]]; then
        remove_json "${path}" servers
      else
        merge_json "${path}" servers "false"
      fi
      ;;
    toml)
      if [[ "${mode}" == "remove" ]]; then
        remove_toml "${path}"
      else
        merge_toml "${path}"
      fi
      ;;
    opencode)
      if [[ "${mode}" == "remove" ]]; then
        remove_opencode "${path}"
      else
        merge_opencode "${path}"
      fi
      ;;
    *)
      echo "Unknown kind: ${kind}" >&2
      exit 1
      ;;
  esac
  echo " - ${path}"
}

IFS=',' read -r -a TOOL_ARR <<< "${TOOLS}"

if [[ "${DRY_RUN}" == true ]]; then
  for tool in "${TOOL_ARR[@]}"; do
    tool="${tool// /}"
    apply_spec "$(config_for_tool "${tool}")" plan
  done
  exit 0
fi

if [[ "${UNINSTALL}" == true ]]; then
  for tool in "${TOOL_ARR[@]}"; do
    tool="${tool// /}"
    apply_spec "$(config_for_tool "${tool}")" remove
  done
  echo "Done."
  exit 0
fi

if [[ "${SKIP_VENV}" != true ]]; then
  if [[ ! -x "${VENV_DIR}/bin/python" && ! -x "${VENV_DIR}/Scripts/python.exe" ]]; then
    python3 -m venv "${VENV_DIR}"
  fi
  "${VENV_PYTHON}" -m pip install --quiet --upgrade pip
  "${VENV_PYTHON}" -m pip install --quiet -r "${SCRIPT_DIR}/requirements.txt"
fi

for tool in "${TOOL_ARR[@]}"; do
  tool="${tool// /}"
  apply_spec "$(config_for_tool "${tool}")" add
done

echo "Done. Restart the client. Cursor/Copilot: enable the cookbook server in MCP settings if it is off."
