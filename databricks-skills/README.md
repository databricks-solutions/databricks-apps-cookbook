# Databricks Apps Skills

AI coding assistant skills for building Databricks Apps. Works with **Cursor** and **Claude Code**.

Each skill teaches your AI assistant how to handle a specific aspect of Databricks Apps development — authentication, table access, volume operations, and more — with framework-specific guidance for Dash, Streamlit, FastAPI, and Reflex.

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

### Option 0a: Claude Code plugin marketplace (recommended for Claude Code)

The repo ships as a Claude Code plugin. Add it as a marketplace and install with two commands — no symlinks, no copies, and the bundled `SessionStart` hook runs automatically.

**From GitHub:**

```text
/plugin marketplace add databricks-solutions/databricks-apps-cookbook
/plugin install databricks-skills@databricks-skills
/reload-plugins
```

**From a local clone (offline / for editing):**

```bash
git clone https://github.com/databricks-solutions/databricks-apps-cookbook.git
```

Then in Claude Code:

```text
/plugin marketplace add /absolute/path/to/databricks-apps-cookbook
/plugin install databricks-skills@databricks-skills
/reload-plugins
```

After install, all 12 skills appear under the `databricks-skills:` namespace (e.g. `databricks-skills:cookbook-authentication`). Manage with:

- `/plugin list` — see installed plugins
- `/plugin marketplace update databricks-skills` — pull latest
- `/plugin uninstall databricks-skills@databricks-skills` — remove

### Option 0b: One-command installer (recommended for Cursor, or for Claude Code without plugins)

Use the included installer to install for Claude Code, Cursor, or both:

```bash
# From repository root
./install.sh claude   # Install skills under ~/.claude/skills/
./install.sh cursor   # Install transformed rules under ~/.cursor/rules/
./install.sh all      # Install for both tools
```

### Option A: Symlink (recommended)

Symlink the entire `databricks-skills` directory so skills stay in sync when you pull updates.

**For Cursor:**

```bash
# Clone the cookbook (if you haven't already)
git clone https://github.com/databricks-solutions/databricks-apps-cookbook.git

# Symlink all skills at once
ln -s "$(pwd)/databricks-apps-cookbook/databricks-skills/authentication" ~/.cursor/skills/cookbook-authentication
ln -s "$(pwd)/databricks-apps-cookbook/databricks-skills/tables" ~/.cursor/skills/cookbook-tables
# ... repeat for each skill you need
```

**For Claude Code:**

```bash
ln -s "$(pwd)/databricks-apps-cookbook/databricks-skills/authentication" ~/.claude/skills/cookbook-authentication
ln -s "$(pwd)/databricks-apps-cookbook/databricks-skills/tables" ~/.claude/skills/cookbook-tables
# ... repeat for each skill you need
```

**Or link all skills at once:**

```bash
# Cursor
for skill in databricks-apps-cookbook/databricks-skills/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/$skill" ~/.cursor/skills/cookbook-"$name"
done

# Claude Code
for skill in databricks-apps-cookbook/databricks-skills/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/$skill" ~/.claude/skills/cookbook-"$name"
done
```

### Option B: Copy

Copy skills into your tool's skill directory. You'll need to re-copy after updates.

```bash
# Cursor
cp -r databricks-apps-cookbook/databricks-skills/authentication ~/.cursor/skills/cookbook-authentication

# Claude Code
cp -r databricks-apps-cookbook/databricks-skills/authentication ~/.claude/skills/cookbook-authentication
```

### Option C: Project-level skills

Place skills directly in your app project so every contributor gets them automatically.

```bash
# Inside your app project
cp -r /path/to/databricks-apps-cookbook/databricks-skills/authentication .cursor/skills/authentication
cp -r /path/to/databricks-apps-cookbook/databricks-skills/authentication .claude/skills/authentication
```

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
