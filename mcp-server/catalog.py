"""Filesystem catalog of cookbook recipes and skills (no Databricks auth)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FRAMEWORKS = ("dash", "streamlit", "reflex", "fastapi")

SAMPLE_ROOTS = {
    "dash": REPO_ROOT / "dash" / "pages",
    "streamlit": REPO_ROOT / "streamlit" / "views",
    "reflex": REPO_ROOT / "reflex" / "app" / "pages",
    "fastapi": REPO_ROOT / "fastapi" / "routes",
}

SKILLS_DIR = REPO_ROOT / "databricks-skills"
DOCS_ROOT = REPO_ROOT / "docs" / "docs"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_FENCE_RE = re.compile(r"```python[^\n]*\n(.*?)```", re.DOTALL)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    return match.group(1).strip() if match else ""


def _first_python_fence(text: str) -> str:
    match = _FENCE_RE.search(text)
    return match.group(1).strip() if match else ""


def _docs_url(framework: str, relative_mdx: str) -> str:
    stem = relative_mdx.removesuffix(".mdx")
    return f"https://apps-cookbook.dev/docs/{framework}/{stem}"


def find_sample_paths(framework: str, slug: str) -> list[str]:
    root = SAMPLE_ROOTS.get(framework)
    if root is None or not root.is_dir():
        return []
    tokens = {t for t in slug.split("_") if t}
    scored: list[tuple[int, Path]] = []
    for path in root.rglob("*.py"):
        if path.name.startswith("_"):
            continue
        stem = path.stem
        stem_tokens = {t for t in stem.split("_") if t}
        score = 0
        if stem == slug:
            score = 100
        elif slug in stem or stem in slug:
            score = 80
        elif tokens and stem_tokens:
            overlap = len(tokens & stem_tokens) / len(tokens | stem_tokens)
            if overlap >= 0.5:
                score = int(overlap * 70)
        if score:
            scored.append((score, path))
    scored.sort(key=lambda item: (-item[0], str(item[1])))
    seen: list[str] = []
    for _, path in scored:
        rel = _rel(path)
        if rel not in seen:
            seen.append(rel)
        if len(seen) == 5:
            break
    return seen


def list_recipes(framework: str | None = None) -> list[dict]:
    frameworks = (framework,) if framework else FRAMEWORKS
    unknown = [name for name in frameworks if name not in FRAMEWORKS]
    if unknown:
        raise ValueError(f"Unknown framework {unknown[0]!r}. Use one of: {', '.join(FRAMEWORKS)}")

    recipes: list[dict] = []
    for name in frameworks:
        docs_dir = DOCS_ROOT / name
        if not docs_dir.is_dir():
            continue
        for mdx in sorted(docs_dir.rglob("*.mdx")):
            rel = mdx.relative_to(docs_dir).as_posix()
            slug = mdx.stem
            if slug in {"index", "intro"}:
                continue
            text = mdx.read_text(encoding="utf-8")
            title_match = _HEADING_RE.search(text)
            category = mdx.parent.relative_to(docs_dir).as_posix()
            if category == ".":
                category = ""
            recipes.append(
                {
                    "framework": name,
                    "slug": slug,
                    "category": category,
                    "title": title_match.group(1).strip() if title_match else slug,
                    "doc_path": _rel(mdx),
                    "docs_url": _docs_url(name, rel),
                    "skill": category.split("/")[0] if category else "",
                }
            )
    return recipes


def get_recipe(framework: str, slug: str) -> dict:
    if framework not in FRAMEWORKS:
        raise ValueError(f"Unknown framework {framework!r}. Use one of: {', '.join(FRAMEWORKS)}")

    docs_dir = DOCS_ROOT / framework
    matches = [path for path in docs_dir.rglob("*.mdx") if path.stem == slug]
    if not matches:
        available = ", ".join(sorted({item["slug"] for item in list_recipes(framework)}))
        raise FileNotFoundError(f"No recipe {slug!r} for {framework}. Available: {available}")

    mdx = matches[0]
    text = mdx.read_text(encoding="utf-8")
    title_match = _HEADING_RE.search(text)
    rel = mdx.relative_to(docs_dir).as_posix()
    category = mdx.parent.relative_to(docs_dir).as_posix()
    if category == ".":
        category = ""
    return {
        "framework": framework,
        "slug": slug,
        "category": category,
        "title": title_match.group(1).strip() if title_match else slug,
        "doc_path": _rel(mdx),
        "docs_url": _docs_url(framework, rel),
        "sample_paths": find_sample_paths(framework, slug),
        "snippet": _first_python_fence(text),
        "resources": _section(text, "Resources"),
        "permissions": _section(text, "Permissions"),
        "dependencies": _section(text, "Dependencies"),
        "skill": category.split("/")[0] if category else "",
    }


def list_skills() -> list[dict]:
    skills: list[dict] = []
    if not SKILLS_DIR.is_dir():
        return skills
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        skills.append(
            {
                "directory": skill_md.parent.name,
                "name": meta.get("name", skill_md.parent.name),
                "description": meta.get("description", ""),
                "path": _rel(skill_md),
            }
        )
    return skills


def get_skill(name: str) -> dict:
    for skill in list_skills():
        if name in {skill["directory"], skill["name"]}:
            text = (REPO_ROOT / skill["path"]).read_text(encoding="utf-8")
            body = _FRONTMATTER_RE.sub("", text, count=1).strip()
            return {**skill, "body": body}
    available = ", ".join(item["directory"] for item in list_skills())
    raise FileNotFoundError(f"Unknown skill {name!r}. Available: {available}")
