import base64
import gradio as gr
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_secret(scope, key):
    try:
        secret_response = w.secrets.get_secret(scope=scope, key=key)
        decoded_secret = base64.b64decode(secret_response.value).decode("utf-8")
        return "Secret retrieved! The value is securely handled in the backend."
    except Exception as e:
        return "Secret not found or inaccessible. Please create a secret scope and key before retrieving."

def create_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Secrets")
        gr.Markdown("## Retrieve a secret")
        gr.Markdown(
            "This recipe retrieves a [Databricks secret](https://docs.databricks.com/en/security/secrets/index.html). "
            "Use secrets to securely connect to external services and APIs."
        )
        
        with gr.Tab("Try it"):
            scope_input = gr.Textbox(label="Secret scope", placeholder="apis")
            key_input = gr.Textbox(label="Secret key", placeholder="weather_service_key")
            retrieve_btn = gr.Button("Retrieve")
            output = gr.Textbox(label="Result")
            
            retrieve_btn.click(
                fn=get_secret,
                inputs=[scope_input, key_input],
                outputs=output
            )
            
        with gr.Tab("Code snippet"):
            gr.Code(
                """
import gradio as gr
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

def get_secret(scope, key):
    try:
        secret_response = w.secrets.get_secret(scope=scope, key=key)
        decoded_secret = base64.b64decode(secret_response.value).decode('utf-8')
        return "Secret retrieved!"
    except Exception as e:
        return "Secret not found or inaccessible."

# Create the interface
demo = gr.Interface(
    fn=get_secret,
    inputs=[
        gr.Textbox(label="Secret scope"),
        gr.Textbox(label="Secret key")
    ],
    outputs=gr.Textbox(label="Result")
)
                """,
                language="python"
            )
            
        with gr.Tab("Requirements"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    **Permissions (app service principal)**
                    * `CAN READ` on the secret scope
                    """)
                with gr.Column():
                    gr.Markdown("""
                    **Databricks resources**
                    * Secret scope
                    """)
                with gr.Column():
                    gr.Markdown("""
                    **Dependencies**
                    * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
                    * [Gradio](https://pypi.org/project/gradio/) - `gradio`
                    """)

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch()