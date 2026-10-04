#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SKILLS_DIR="${SCRIPT_DIR}/databricks-skills"

# Allow overrides for testing/dry-runs.
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-${HOME}/.claude/skills}"
CURSOR_RULES_DIR="${CURSOR_RULES_DIR:-${HOME}/.cursor/rules}"

usage() {
  cat <<'EOF'
Usage: ./install.sh [claude|cursor|all]

Modes:
  claude   Copy databricks skills directories into ~/.claude/skills/
  cursor   Convert SKILL.md files into Cursor rules under ~/.cursor/rules/
  all      Install for both Claude Code and Cursor (default)
EOF
}

ensure_source_exists() {
  if [[ ! -d "${SOURCE_SKILLS_DIR}" ]]; then
    echo "ERROR: Skills source directory not found: ${SOURCE_SKILLS_DIR}" >&2
    exit 1
  fi
}

strip_skill_frontmatter() {
  local skill_file="$1"
  awk '
    NR == 1 && $0 == "---" { in_frontmatter = 1; next }
    in_frontmatter && $0 == "---" { in_frontmatter = 0; next }
    !in_frontmatter { print }
  ' "${skill_file}"
}

extract_frontmatter_value() {
  local skill_file="$1"
  local key="$2"
  awk -v lookup_key="${key}" '
    NR == 1 && $0 == "---" { in_frontmatter = 1; next }
    in_frontmatter && $0 == "---" { exit }
    in_frontmatter && $1 == (lookup_key ":") {
      sub(/^[^:]+:[[:space:]]*/, "")
      print
      exit
    }
  ' "${skill_file}"
}

install_for_claude() {
  mkdir -p "${CLAUDE_SKILLS_DIR}"
  echo "Installing skills to ${CLAUDE_SKILLS_DIR}"

  for skill_dir in "${SOURCE_SKILLS_DIR}"/*; do
    [[ -d "${skill_dir}" ]] || continue
    skill_name="$(basename "${skill_dir}")"
    target_dir="${CLAUDE_SKILLS_DIR}/${skill_name}"
    rm -rf "${target_dir}"
    cp -R "${skill_dir}" "${target_dir}"
    echo " - Installed Claude skill: ${skill_name}"
  done
}

install_for_cursor() {
  mkdir -p "${CURSOR_RULES_DIR}"
  echo "Installing transformed rules to ${CURSOR_RULES_DIR}"

  for skill_dir in "${SOURCE_SKILLS_DIR}"/*; do
    [[ -d "${skill_dir}" ]] || continue
    skill_name="$(basename "${skill_dir}")"
    skill_file="${skill_dir}/SKILL.md"
    [[ -f "${skill_file}" ]] || continue

    frontmatter_name="$(extract_frontmatter_value "${skill_file}" "name")"
    frontmatter_description="$(extract_frontmatter_value "${skill_file}" "description")"
    frontmatter_name="${frontmatter_name%\"}"
    frontmatter_name="${frontmatter_name#\"}"
    frontmatter_description="${frontmatter_description%\"}"
    frontmatter_description="${frontmatter_description#\"}"

    if [[ -z "${frontmatter_name}" ]]; then
      frontmatter_name="${skill_name}"
    fi
    if [[ -z "${frontmatter_description}" ]]; then
      frontmatter_description="Imported rule from databricks-skills/${skill_name}/SKILL.md"
    fi

    escaped_description="${frontmatter_description//\"/\\\"}"
    target_rule="${CURSOR_RULES_DIR}/${frontmatter_name}.mdc"

    {
      echo "---"
      echo "description: \"${escaped_description}\""
      echo "alwaysApply: false"
      echo "---"
      strip_skill_frontmatter "${skill_file}"
    } > "${target_rule}"

    echo " - Installed Cursor rule: $(basename "${target_rule}")"
  done
}

ensure_source_exists

case "${MODE}" in
  claude)
    install_for_claude
    ;;
  cursor)
    install_for_cursor
    ;;
  all)
    install_for_claude
    install_for_cursor
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "ERROR: Invalid mode '${MODE}'" >&2
    usage
    exit 1
    ;;
esac

echo "Done."
