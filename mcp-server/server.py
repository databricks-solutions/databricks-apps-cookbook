"""Cookbook MCP tools for coding agents. Local recipes/skills only — not Databricks workspace tools."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from catalog import FRAMEWORKS, get_recipe, get_skill, list_recipes, list_skills

mcp = FastMCP("cookbook")


@mcp.tool()
def list_cookbook_recipes(framework: str | None = None) -> dict:
    """List Databricks Apps Cookbook recipes (Dash, Streamlit, Reflex, FastAPI).

    Optional framework filter: dash, streamlit, reflex, fastapi.
    Returns slug, title, doc_path, docs_url, and category. Call get_cookbook_recipe
    for the snippet, permissions, and sample file paths.
    This is not Databricks managed MCP (SQL/UC/Genie). Those come from Unity Gateway.
    """
    recipes = list_recipes(framework)
    return {"frameworks": list(FRAMEWORKS), "count": len(recipes), "recipes": recipes}


@mcp.tool()
def get_cookbook_recipe(framework: str, slug: str) -> dict:
    """Get one cookbook recipe: Python snippet, permissions, resources, sample paths.

    framework: dash | streamlit | reflex | fastapi
    slug: mdx stem, e.g. tables_read, mcp_connect, users_get_current
    Implementations must use these snippets/samples, not invented AppKit code.
    """
    return get_recipe(framework, slug)


@mcp.tool()
def list_cookbook_skills() -> dict:
    """List cookbook composition skills (build-app, tables, authentication, …).

    Load build-app first when scaffolding a Dash/Streamlit/Reflex/FastAPI app.
    """
    skills = list_skills()
    return {"count": len(skills), "skills": skills}


@mcp.tool()
def get_cookbook_skill(name: str) -> dict:
    """Get a cookbook SKILL.md by directory or frontmatter name (e.g. build-app, cookbook-tables)."""
    return get_skill(name)
