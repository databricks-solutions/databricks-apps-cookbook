import gradio as gr
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieMessage
import pandas as pd
from typing import Dict, List, Tuple

w = WorkspaceClient()

def reset_conversation() -> Tuple[str, List]:
    global conversation_id
    conversation_id = None
    return "", []

def get_query_result(statement_id: str) -> pd.DataFrame:     
    query = w.statement_execution.get_statement(statement_id)
    result = query.result.data_array

    next_chunk = query.result.next_chunk_index
    while next_chunk:
        chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, next_chunk)
        result.append(chunk.data_array)
        next_chunk = chunk.next_chunk_index

    return pd.DataFrame(result, columns=[i.name for i in query.manifest.schema.columns])

def process_message(response: GenieMessage) -> List[Tuple]:
    global conversation_id
    conversation_id = response.conversation_id
    messages = []
    
    for attachment in response.attachments:
        if attachment.text:
            messages.append(("assistant", attachment.text.content))
        elif attachment.query:
            data = get_query_result(attachment.query.statement_id)
            # Convert DataFrame to string representation for display
            data_str = f"```\n{data.to_string()}\n```"
            description = attachment.query.description
            code = f"\nGenerated SQL:\n```sql\n{attachment.query.query}\n```"
            messages.append(("assistant", f"{description}\n{data_str}{code}"))
    
    return messages

def chat(message: str, history: List, genie_space_id: str) -> Tuple[str, List]:
    if not genie_space_id:
        return "Please fill in the Genie Space ID.", history
    
    try:
        if conversation_id:
            response = w.genie.create_message_and_wait(
                genie_space_id, conversation_id, message
            )
        else:
            response = w.genie.start_conversation_and_wait(genie_space_id, message)
        
        if response.error:
            return f"Error: {response.error.type} - {response.error.error}", history
        
        new_messages = process_message(response)
        assistant_response = "\n".join([msg[1] for msg in new_messages])
        history.append((message, assistant_response))
        
        return "", history
    
    except Exception as e:
        error_msg = "Failed to initialize Genie. Check the required permissions."
        return error_msg, history

# Initialize global conversation ID
conversation_id = None

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Genie\n## Converse with your data")
    gr.Markdown("""
    This app uses [Genie](https://www.databricks.com/product/ai-bi) [API](https://docs.databricks.com/api/workspace/genie) 
    to let users ask questions about your data for instant insights.
    """)
    
    with gr.Row():
        genie_space_id = gr.Textbox(
            label="Genie Space ID",
            placeholder="01efe16a65e21836acefb797ae6a8fe4",
            info="Room ID in the Genie Space URL"
        )
    
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Ask your question...")
    
    with gr.Row():
        submit = gr.Button("Submit")
        clear = gr.Button("New Chat")
    
    # Event handlers
    msg.submit(chat, [msg, chatbot, genie_space_id], [msg, chatbot])
    submit.click(chat, [msg, chatbot, genie_space_id], [msg, chatbot])
    clear.click(reset_conversation, None, [msg, chatbot])

if __name__ == "__main__":
    demo.launch()