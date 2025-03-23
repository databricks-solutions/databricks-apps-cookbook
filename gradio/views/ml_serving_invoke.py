import gradio as gr
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from json import loads

w = WorkspaceClient()

def get_endpoint_names():
    endpoints = w.serving_endpoints.list()
    return [endpoint.name for endpoint in endpoints]

def invoke_llm(model_name, prompt, temperature):
    response = w.serving_endpoints.query(
        name=model_name,
        messages=[
            ChatMessage(
                role=ChatMessageRole.SYSTEM,
                content="You are a helpful assistant.",
            ),
            ChatMessage(
                role=ChatMessageRole.USER,
                content=prompt,
            ),
        ],
        temperature=temperature,
    )
    return str(response.as_dict())

def invoke_ml_model(model_name, input_json):
    try:
        input_data = loads(input_json)
        response = w.serving_endpoints.query(
            name=model_name,
            dataframe_records=input_data
        )
        return str(response.as_dict())
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="ML Model Serving Interface") as demo:
    gr.Markdown("# AI / ML Model Serving")
    gr.Markdown("This interface invokes models hosted on Mosaic AI Model Serving and returns the result.")
    
    endpoint_names = get_endpoint_names()
    
    with gr.Tab("LLM"):
        model_dropdown_llm = gr.Dropdown(choices=endpoint_names, label="Select Model")
        temperature = gr.Slider(minimum=0.0, maximum=2.0, value=1.0, step=0.1, 
                              label="Temperature", info="Controls the randomness of the LLM output")
        prompt = gr.Textbox(label="Enter your prompt", lines=3)
        submit_btn_llm = gr.Button("Invoke LLM")
        output_llm = gr.JSON(label="Response")
        
        submit_btn_llm.click(
            fn=invoke_llm,
            inputs=[model_dropdown_llm, prompt, temperature],
            outputs=output_llm
        )
    
    with gr.Tab("Traditional ML"):
        model_dropdown_ml = gr.Dropdown(choices=endpoint_names, label="Select Model")
        input_json = gr.Textbox(
            label="Enter model input (JSON)", 
            lines=3,
            placeholder='{"feature1": [1.5], "feature2": [2.5]}'
        )
        submit_btn_ml = gr.Button("Invoke Model")
        output_ml = gr.JSON(label="Response")
        
        info_text = """
        The model has to be deployed to Mosaic AI Model Serving. 
        Request pattern corresponds to the model signature registered in Unity Catalog.
        """
        gr.Markdown(info_text)
        
        submit_btn_ml.click(
            fn=invoke_ml_model,
            inputs=[model_dropdown_ml, input_json],
            outputs=output_ml
        )

if __name__ == "__main__":
    demo.launch()