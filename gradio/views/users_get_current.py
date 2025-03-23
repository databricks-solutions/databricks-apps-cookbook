import gradio as gr
from flask import request

def get_user_info():
    # Get headers from the request
    headers = request.headers
    email = headers.get("X-Forwarded-Email")
    username = headers.get("X-Forwarded-Preferred-Username")
    ip = headers.get("X-Real-Ip")
    
    # Format user details
    user_details = f"""
    #### User Details
    
    E-mail: {email}
    Username: {username}
    IP Address: {ip}
    """
    
    # Convert headers to dictionary for JSON display
    all_headers = dict(headers)
    
    return user_details, str(all_headers)

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Users")
    gr.Markdown("### Get current user")
    gr.Markdown("This recipe gets information about the user accessing this Databricks App from their [HTTP headers](https://docs.databricks.com/en/dev-tools/databricks-apps/app-development.html#what-http-headers-are-passed-to-databricks-apps).")
    
    with gr.Tab("Try it"):
        user_info = gr.Markdown()
        headers_json = gr.JSON()
        # Auto-run when the page loads
        demo.load(get_user_info, outputs=[user_info, headers_json])
    
    with gr.Tab("Code snippet"):
        gr.Code("""
import gradio as gr
from flask import request

headers = request.headers
email = headers.get("X-Forwarded-Email")
username = headers.get("X-Forwarded-Preferred-Username")
user = headers.get("X-Forwarded-User")
ip = headers.get("X-Real-Ip")

print(f"E-mail: {email}, username: {username}, user: {user}, ip: {ip}")
        """, language="python")
        
        gr.Markdown("""
#### Other frameworks
* **Dash, Flask**: use [`request.headers`](https://flask.palletsprojects.com/en/stable/api/#flask.Request.headers) from `flask` Python library.
        """)
    
    with gr.Tab("Requirements"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                **Permissions (app service principal)**
                
                No permissions needed
                """)
            with gr.Column():
                gr.Markdown("""
                **Databricks resources**
                
                None
                """)
            with gr.Column():
                gr.Markdown("""
                **Dependencies**
                * Gradio - `gradio`
                * Flask - `flask`
                """)

if __name__ == "__main__":
    demo.launch()