import os
import gradio as gr
from databricks.sdk import WorkspaceClient

def download_file(file_path):
    if not file_path:
        return (None, "Please specify a file path.")
    
    try:
        w = WorkspaceClient()
        resp = w.files.download(file_path)
        file_data = resp.contents.read()
        file_name = os.path.basename(file_path)
        
        # Save the file temporarily to allow Gradio to serve it
        temp_path = f"/tmp/{file_name}"
        with open(temp_path, "wb") as f:
            f.write(file_data)
            
        return (temp_path, f"File '{file_name}' downloaded successfully")
    except Exception as e:
        return (None, f"Error downloading file: {str(e)}")

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Volumes")
    gr.Markdown("## Download a file")
    gr.Markdown("This recipe downloads a file from a [Unity Catalog volume](https://docs.databricks.com/en/volumes/index.html).")
    
    with gr.Tab("Try it"):
        file_path = gr.Textbox(
            label="Specify a path to a file in a Unity Catalog volume",
            placeholder="/Volumes/main/marketing/raw_files/leads.csv"
        )
        download_btn = gr.Button("Get file")
        output_file = gr.File(label="Downloaded file")
        status_msg = gr.Markdown()
        
        download_btn.click(
            fn=download_file,
            inputs=[file_path],
            outputs=[output_file, status_msg]
        )
    
    with gr.Tab("Requirements"):
        gr.Markdown("""
        **Permissions (app service principal)**
        * `USE CATALOG` on the volume's catalog
        * `USE SCHEMA` on the volume's schema
        * `READ VOLUME` on the volume
        
        **Databricks resources**
        * Unity Catalog volume
        
        **Dependencies**
        * Databricks SDK for Python - `databricks-sdk`
        * Gradio - `gradio`
        """)

if __name__ == "__main__":
    demo.launch()