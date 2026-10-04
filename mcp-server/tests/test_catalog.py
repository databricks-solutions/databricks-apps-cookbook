from catalog import FRAMEWORKS, get_recipe, get_skill, list_recipes, list_skills


def test_list_recipes_all_frameworks():
    recipes = list_recipes()
    assert {item["framework"] for item in recipes} == set(FRAMEWORKS)
    slugs = {(item["framework"], item["slug"]) for item in recipes}
    assert ("streamlit", "tables_read") in slugs
    assert ("dash", "mcp_connect") in slugs


def test_get_recipe_includes_snippet_and_permissions():
    recipe = get_recipe("streamlit", "tables_read")
    assert "sql.connect" in recipe["snippet"]
    assert "SELECT" in recipe["permissions"]
    assert "streamlit/views/tables_read.py" in recipe["sample_paths"]
    assert recipe["doc_path"].endswith("tables_read.mdx")


def test_skills_include_build_app():
    names = {item["directory"] for item in list_skills()}
    assert "build-app" in names
    skill = get_skill("build-app")
    assert "When not to use this skill" in skill["body"]
