import gradio as gr
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()

def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()

def insert_overwrite_table(table_name: str, df: pd.DataFrame, conn):
    with conn.cursor() as cursor:
        rows = list(df.itertuples(index=False))
        values = ",".join([f"({','.join(map(repr, row))})" for row in rows])
        cursor.execute(f"INSERT OVERWRITE {table_name} VALUES {values}")
    return "Changes saved successfully!"

def process_table(http_path: str, table_name: str):
    if not http_path or not table_name:
        return None, "Please provide both warehouse path and table name."
    
    try:
        conn = get_connection(http_path)
        df = read_table(table_name, conn)
        return df, "Table loaded successfully!"
    except Exception as e:
        return None, f"Error: {str(e)}"

def save_changes(http_path: str, table_name: str, df: pd.DataFrame):
    if df is None:
        return "No data to save!"
    
    try:
        conn = get_connection(http_path)
        result = insert_overwrite_table(table_name, df, conn)
        return result
    except Exception as e:
        return f"Error saving changes: {str(e)}"

# Create the Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# Tables")
    gr.Markdown("## Edit a table")
    gr.Markdown(
        "Use this recipe to read, edit, and write back data stored in a small Unity Catalog table "
        "with [Databricks SQL Connector](https://docs.databricks.com/en/dev-tools/python-sql-connector.html)."
    )
    
    with gr.Row():
        http_path_input = gr.Textbox(
            label="HTTP Path to Databricks SQL Warehouse",
            placeholder="/sql/1.0/warehouses/xxxxxx"
        )
        table_name_input = gr.Textbox(
            label="Catalog table name",
            placeholder="catalog.schema.table"
        )
    
    load_btn = gr.Button("Load Table")
    status_output = gr.Textbox(label="Status")
    
    dataframe = gr.Dataframe(
        headers=None,
        datatype=None,
        col_count=None,
        row_count=None,
        interactive=True,
        visible=False
    )
    
    save_btn = gr.Button("Save Changes", visible=False)
    
    # Event handlers
    load_btn.click(
        fn=process_table,
        inputs=[http_path_input, table_name_input],
        outputs=[dataframe, status_output]
    ).then(
        lambda: (True, True),
        None,
        [dataframe.visible, save_btn.visible]
    )
    
    save_btn.click(
        fn=save_changes,
        inputs=[http_path_input, table_name_input, dataframe],
        outputs=[status_output]
    )

if __name__ == "__main__":
    app.launch()