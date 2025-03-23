import gradio as gr
from view_groups import groups

def create_demo():
    with gr.Blocks() as demo:
        gr.Markdown(
            """
            **Welcome to the Databricks Apps Cookbook!**

            Are you ready to serve some tasty apps to your users? You're in the right place!  
            
            Explore the recipes to quickly build flexible and engaging data apps directly on Databricks.

            Have a great recipe to share? Raise a pull request on the [GitHub repository](https://github.com/pbv0/databricks-apps-cookbook)!
            """
        )

        gr.Markdown("## Recipes")
        
        # Filter groups that have titles
        filtered_groups = [group for group in groups if group.get("title")]
        
        # Create grid layout
        with gr.Row():
            for i in range(0, len(filtered_groups), 4):
                group_chunk = filtered_groups[i:i+4]
                for group in group_chunk:
                    with gr.Column():
                        gr.Markdown(f"**{group['title']}**")
                        for view in group["views"]:
                            gr.Markdown(f"- [{view['label']}]({view['page']})")

        gr.Markdown("## Links")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown(
                    """
                    #### Official documentation
                    - [AWS](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
                    - [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/)
                    - [Python SDK](https://databricks-sdk-py.readthedocs.io/en/latest/)
                    """
                )
            
            with gr.Column():
                gr.Markdown(
                    """
                    #### Code samples
                    - [Databricks Apps Templates](https://github.com/databricks/app-templates)
                    """
                )
            
            with gr.Column():
                gr.Markdown(
                    """
                    #### Blog posts
                    - [End-to-end RAG application](https://www.linkedin.com/pulse/end-to-end-rag-application-source-retriveal-platform-ivan-trusov-znvqf/)
                    - [Building data applications](https://www.linkedin.com/pulse/building-data-applications-databricks-apps-ivan-trusov-6pjwf/)
                    """
                )

    return demo