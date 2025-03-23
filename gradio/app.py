import gradio as gr
from view_groups import groups
import importlib

def load_demo(module_path):
    module = importlib.import_module(module_path)
    return module.create_demo()

def create_app():
    with gr.Blocks(theme=gr.themes.Soft()) as app:
        gr.Markdown("# 📖 Databricks Apps Cookbook 🍳")
        
        # Create tabs for each group
        with gr.Tabs() as tabs:
            for group in groups:
                if "title" in group:
                    with gr.Tab(group["title"]):
                        for view in group["views"]:
                            demo = load_demo(view["page"].replace(".py", ""))

    return app

if __name__ == "__main__":
    app = create_app()
    app.launch()