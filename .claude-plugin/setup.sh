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

if [[ -d "${HOME}/.cursor" || -d "${HOME}/.cursor/rules" ]]; then
  echo "[databricks-skills] Cursor detected."
  echo "[databricks-skills] Run ./install.sh cursor to install transformed rules for Cursor."
else
  echo "[databricks-skills] Run ./install.sh claude to install skills for Claude Code."
  echo "[databricks-skills] Run ./install.sh all to install for both Claude Code and Cursor."
fi
