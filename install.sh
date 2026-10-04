#!/usr/bin/env bash
# Install cookbook skills using the same project vs --global layout as AI Dev Kit.
# Source of truth is databricks-skills/<name>/SKILL.md in this clone.
#
# Upgrade: git pull this repo, then re-run the same command (overwrites in place).
# Claude Code plugin users: /plugin marketplace update databricks-skills
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILLS_DIR="${SCRIPT_DIR}/databricks-skills"

DEFAULT_TOOLS="claude,cursor,copilot,codex,gemini,antigravity,windsurf,opencode,kiro"
TOOLS="${DEFAULT_TOOLS}"
SCOPE="project"
TARGET_DIR="$(pwd)"
UNINSTALL=false
DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: ./install.sh [options] [claude|cursor|all]

Install Dash/Streamlit/Reflex/FastAPI cookbook skills. Paths match AI Dev Kit
(project vs --global). Re-run after `git pull` to upgrade.

  --tools LIST     claude,cursor,copilot,codex,gemini,antigravity,windsurf,opencode,kiro
                   (default: all of the above)
  -g, --global     User-level dirs under $HOME (all repos on this machine)
  --target-dir DIR Project-scope root (default: current directory)
  --uninstall      Remove cookbook skill folders only (same scope/tools)
  --dry-run        Print target directories and exit
  -h, --help

Legacy: ./install.sh claude|cursor|all  (same as --tools)

Claude Code plugin (no copy): see databricks-skills/README.md
Recipe MCP: ./mcp-server/mcp_install.sh
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tools) TOOLS="$2"; shift 2 ;;
    -g|--global) SCOPE="global"; shift ;;
    --target-dir) TARGET_DIR="$2"; shift 2 ;;
    --uninstall) UNINSTALL=true; shift ;;
    --dry-run) DRY_RUN=true; shift ;;
    -h|--help|help) usage; exit 0 ;;
    claude|cursor|copilot|codex|gemini|antigravity|windsurf|opencode|kiro)
      TOOLS="$1"
      shift
      ;;
    all)
      TOOLS="${DEFAULT_TOOLS}"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! -d "${SOURCE_SKILLS_DIR}" ]]; then
  echo "ERROR: Skills source directory not found: ${SOURCE_SKILLS_DIR}" >&2
  exit 1
fi

if [[ "${SCOPE}" == "global" ]]; then
  BASE_DIR="${HOME}"
else
  mkdir -p "${TARGET_DIR}"
  TARGET_DIR="$(cd "${TARGET_DIR}" && pwd)"
  BASE_DIR="${TARGET_DIR}"
fi

# Same dest layout as AI Dev Kit install.sh agent_skill_target_dirs.
skill_dir_for_tool() {
  local tool="$1"
  case "${tool}" in
    claude) echo "${BASE_DIR}/.claude/skills" ;;
    cursor) echo "${BASE_DIR}/.cursor/skills" ;;
    copilot) echo "${BASE_DIR}/.github/skills" ;;
    codex) echo "${BASE_DIR}/.agents/skills" ;;
    gemini) echo "${BASE_DIR}/.gemini/skills" ;;
    antigravity)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.gemini/antigravity/skills"
      else
        echo "${BASE_DIR}/.agents/skills"
      fi
      ;;
    windsurf)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.codeium/windsurf/skills"
      else
        echo "${BASE_DIR}/.windsurf/skills"
      fi
      ;;
    opencode)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.config/opencode/skills"
      else
        echo "${BASE_DIR}/.opencode/skills"
      fi
      ;;
    kiro)
      if [[ "${SCOPE}" == "global" ]]; then
        echo "${HOME}/.kiro/skills"
      else
        echo "${BASE_DIR}/.kiro/skills"
      fi
      ;;
    *)
      echo "Unknown tool: ${tool}" >&2
      exit 1
      ;;
  esac
}

skill_names() {
  local d
  for d in "${SOURCE_SKILLS_DIR}"/*; do
    [[ -d "${d}" && -f "${d}/SKILL.md" ]] || continue
    basename "${d}"
  done
}

legacy_cursor_rules_cleanup() {
  local rules_dir="${HOME}/.cursor/rules"
  [[ -d "${rules_dir}" ]] || return 0
  local name
  while IFS= read -r name; do
    [[ -n "${name}" ]] || continue
    rm -f "${rules_dir}/${name}.mdc" "${rules_dir}/cookbook-${name}.mdc"
  done < <(skill_names)
}

echo "Cookbook skills"
echo "  source: ${SOURCE_SKILLS_DIR}"
echo "  scope:  ${SCOPE}"
echo "  target: ${BASE_DIR}"
echo "  tools:  ${TOOLS}"

IFS=',' read -r -a TOOL_ARR <<< "${TOOLS}"

DEST_DIRS_FILE="$(mktemp)"
trap 'rm -f "${DEST_DIRS_FILE}"' EXIT
for tool in "${TOOL_ARR[@]}"; do
  tool="${tool// /}"
  [[ -n "${tool}" ]] || continue
  skill_dir_for_tool "${tool}"
done | sort -u > "${DEST_DIRS_FILE}"

if [[ "${DRY_RUN}" == true ]]; then
  while IFS= read -r dest; do
    echo " - ${dest}"
  done < "${DEST_DIRS_FILE}"
  exit 0
fi

if [[ "${UNINSTALL}" == true ]]; then
  while IFS= read -r dest; do
    while IFS= read -r name; do
      [[ -n "${name}" ]] || continue
      if [[ -e "${dest}/${name}" ]]; then
        rm -rf "${dest}/${name}"
        echo " - removed ${dest}/${name}"
      fi
    done < <(skill_names)
  done < "${DEST_DIRS_FILE}"
  for tool in "${TOOL_ARR[@]}"; do
    tool="${tool// /}"
    if [[ "${tool}" == "cursor" ]]; then
      legacy_cursor_rules_cleanup
    fi
  done
  echo "Done."
  exit 0
fi

while IFS= read -r name; do
  [[ -n "${name}" ]] || continue
  src="${SOURCE_SKILLS_DIR}/${name}"
  while IFS= read -r dest; do
    mkdir -p "${dest}"
    rm -rf "${dest}/${name}"
    cp -R "${src}" "${dest}/${name}"
    echo " - ${dest}/${name}"
  done < "${DEST_DIRS_FILE}"
done < <(skill_names)

for tool in "${TOOL_ARR[@]}"; do
  tool="${tool// /}"
  if [[ "${tool}" == "cursor" ]]; then
    legacy_cursor_rules_cleanup
  fi
done

echo "Done. Re-run this command after git pull to upgrade. Recipe MCP: ./mcp-server/mcp_install.sh"
