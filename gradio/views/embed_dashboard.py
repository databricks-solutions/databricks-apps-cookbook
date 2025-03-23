import gradio as gr

def embed_dashboard(iframe_url):
    if not iframe_url:
        return None
    
    # Gradio's HTML component can be used to embed iframes
    iframe_html = f"""
    <iframe 
        src="{iframe_url}"
        width="700"
        height="600"
        style="border: none;"
        scrolling="yes">
    </iframe>
    """
    return iframe_html

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Data Visualization")
    gr.Markdown("## AI/BI Dashboard")
    gr.Markdown("""
    This recipe uses [Databricks AI/BI](https://www.databricks.com/product/ai-bi) to embed a dashboard into a Databricks App.
    """)
    
    with gr.Tab("Try it"):
        url_input = gr.Textbox(
            label="Embed the dashboard:",
            placeholder="https://dbc-f0e9b24f-3d49.cloud.databricks.com/embed/dashboardsv3/01eff8112e9411cd930f0ae0d2c6b63d?o=37581543725667790",
            info="Copy and paste the URL from the dashboard UI Share -> Embed iframe."
        )
        output = gr.HTML()
        url_input.change(fn=embed_dashboard, inputs=url_input, outputs=output)
    
    with gr.Tab("Code snippet"):
        gr.Code("""
import gradio as gr

def embed_dashboard(iframe_url):
    iframe_html = f'''
    <iframe 
        src="{iframe_url}"
        width="700"
        height="600"
        style="border: none;"
        scrolling="yes">
    </iframe>
    '''
    return iframe_html
        """, language="python")
    
    with gr.Tab("Requirements"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                **Permissions (app service principal)**
                * `CAN VIEW` permission on the dashboard
                """)
            with gr.Column():
                gr.Markdown("""
                **Databricks resources**
                * SQL Warehouse
                """)
            with gr.Column():
                gr.Markdown("""
                **Dependencies**
                * [Gradio](https://pypi.org/project/gradio/) - `gradio`
                """)
        
        gr.Warning("⚠️ A workspace admin needs to enable dashboard embedding in the Security settings of your Databricks workspace for specific domains (e.g., databricksapps.com) or all domains for this sample to work.")

if __name__ == "__main__":
    demo.launch()