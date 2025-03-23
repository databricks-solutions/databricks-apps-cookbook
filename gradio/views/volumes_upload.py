import os
import io
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import SecurableType
import gradio as gr

databricks_host = os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_HOSTNAME")
w = WorkspaceClient()

def check_upload_permissions(volume_name: str):
    try:
        volume = w.volumes.read(name=volume_name)
        current_user = w.current_user.me()
        grants = w.grants.get_effective(
            securable_type=SecurableType.VOLUME,
            full_name=volume.full_name,
            principal=current_user.user_name,
        )

        if not grants or not grants.privilege_assignments:
            return "Insufficient permissions: No grants found."

        for assignment in grants.privilege_assignments:
            for privilege in assignment.privileges:
                if privilege.privilege.value in ["ALL_PRIVILEGES", "WRITE_VOLUME"]:
                    return "Volume and permissions validated"

        return "Insufficient permissions: Required privileges not found."
    except Exception as e:
        return f"Error: {e}"

def upload_file(volume_path: str, file_obj: gr.File):
    if not volume_path.strip():
        return "Please specify a valid Volume path."
    if not file_obj:
        return "Please pick a file to upload."
    
    try:
        file_bytes = file_obj.read()
        binary_data = io.BytesIO(file_bytes)
        file_name = os.path.basename(file_obj.name)
        parts = volume_path.strip().split(".")
        catalog = parts[0]
        schema = parts[1]
        volume_name = parts[2]
        volume_file_path = f"/Volumes/{catalog}/{schema}/{volume_name}/{file_name}"
        
        w.files.upload(volume_file_path, binary_data, overwrite=True)
        volume_url = f"https://{databricks_host}/explore/data/volumes/{catalog}/{schema}/{volume_name}"
        return f"File '{file_name}' successfully uploaded to {volume_path}. Volume URL: {volume_url}"
    except Exception as e:
        return f"Error uploading file: {e}"

def check_and_enable_upload(volume_path: str):
    result = check_upload_permissions(volume_path.strip())
    if result == "Volume and permissions validated":
        return {
            permission_output: result,
            file_upload: gr.update(interactive=True),
            upload_button: gr.update(interactive=True)
        }
    else:
        return {
            permission_output: result,
            file_upload: gr.update(interactive=False),
            upload_button: gr.update(interactive=False)
        }

with gr.Blocks(title="Volumes Upload") as app:
    gr.Markdown("# Volumes")
    gr.Markdown("This recipe uploads a file to a [Unity Catalog Volume](https://docs.databricks.com/en/volumes/index.html).")
    
    with gr.Tab("Try it"):
        volume_input = gr.Textbox(
            label="Specify a Unity Catalog Volume name:",
            placeholder="main.marketing.raw_files"
        )
        check_button = gr.Button("Check Volume and permissions")
        permission_output = gr.Textbox(label="Permission Status", interactive=False)
        
        file_upload = gr.File(label="Pick a file to upload", interactive=False)
        upload_button = gr.Button("Upload file", interactive=False)
        upload_output = gr.Textbox(label="Upload Status", interactive=False)
        
        check_button.click(
            fn=check_and_enable_upload,
            inputs=[volume_input],
            outputs=[permission_output, file_upload, upload_button]
        )
        
        upload_button.click(
            fn=upload_file,
            inputs=[volume_input, file_upload],
            outputs=upload_output
        )
    
    with gr.Tab("Requirements"):
        gr.Markdown("""
        **Permissions (app service principal)**
        * `USE CATALOG` on the catalog of the volume
        * `USE SCHEMA` on the schema of the volume
        * `READ VOLUME` and `WRITE VOLUME` on the volume

        **Databricks resources**
        * Unity Catalog volume

        **Dependencies**
        * Databricks SDK for Python - `databricks-sdk`
        * Gradio - `gradio`
        """)

if __name__ == "__main__":
    app.launch()