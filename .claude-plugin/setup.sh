#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SKILLS_DIR="${REPO_ROOT}/databricks-skills"

echo "[databricks-skills] Plugin installed."

if [[ -d "${SKILLS_DIR}" ]]; then
  echo "[databricks-skills] Available skills:"
  while IFS= read -r skill_dir; do
    skill_name="$(basename "${skill_dir}")"
    echo " - ${skill_name}"
  done < <(ls -1d "${SKILLS_DIR}"/*/ 2>/dev/null | sort)
else
  echo "[databricks-skills] Skills directory not found: ${SKILLS_DIR}"
fi

echo "[databricks-skills] Cursor/Claude copies: ./install.sh --global   (or --target-dir for one repo)"
echo "[databricks-skills] Recipe MCP: ./mcp-server/mcp_install.sh"
echo "[databricks-skills] Upgrade: git pull, then re-run the same install command (or /plugin marketplace update databricks-skills)."
