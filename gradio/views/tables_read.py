import gradio as gr
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

def process_table_request(http_path, table_name):
    if not http_path or not table_name:
        return None
    try:
        conn = get_connection(http_path)
        df = read_table(table_name, conn)
        return df
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Tables")
    gr.Markdown("## Read a table")
    gr.Markdown("This recipe reads a Unity Catalog table using the [Databricks SQL Connector](https://docs.databricks.com/en/dev-tools/python-sql-connector.html).")
    
    with gr.Tab("Try it"):
        http_path_input = gr.Textbox(
            label="Enter your Databricks HTTP Path:",
            placeholder="/sql/1.0/warehouses/xxxxxx"
        )
        table_name_input = gr.Textbox(
            label="Specify a Unity Catalog table name:",
            placeholder="catalog.schema.table"
        )
        output = gr.Dataframe()
        
        submit_btn = gr.Button("Read Table")
        submit_btn.click(
            fn=process_table_request,
            inputs=[http_path_input, table_name_input],
            outputs=output
        )
    
    with gr.Tab("Requirements"):
        gr.Markdown("""
        **Permissions (app service principal)**
        * `SELECT` on the Unity Catalog table
        * `CAN USE` on the SQL warehouse
        
        **Databricks resources**
        * SQL warehouse
        * Unity Catalog table
        
        **Dependencies**
        * [Databricks SDK](https://pypi.org/project/databricks-sdk/) - `databricks-sdk`
        * [Databricks SQL Connector](https://pypi.org/project/databricks-sql-connector/) - `databricks-sql-connector`
        * [Gradio](https://pypi.org/project/gradio/) - `gradio`
        """)

if __name__ == "__main__":
    demo.launch()