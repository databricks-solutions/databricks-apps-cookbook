import os
import gradio as gr
import pandas as pd
from databricks.connect import DatabricksSession

def connect_to_cluster(cluster_id: str):
    server_hostname = os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_HOSTNAME")
    return DatabricksSession.builder.remote(
        host=server_hostname, cluster_id=cluster_id
    ).getOrCreate()

def handle_python_compute(cluster_id: str, num_points: int):
    if not cluster_id:
        return "Please provide a cluster ID", None
    
    try:
        spark = connect_to_cluster(cluster_id)
        df = spark.range(num_points).toPandas()
        session_info = {
            "App Name": spark.conf.get("spark.app.name", "Unknown"),
            "Master URL": spark.conf.get("spark.master", "Unknown"),
        }
        return str(session_info), df
    except Exception as e:
        return f"Error: {str(e)}", None

def handle_sql_compute(cluster_id: str, operation: str):
    if not cluster_id:
        return "Please provide a cluster ID", None
    
    try:
        spark = connect_to_cluster(cluster_id)
        
        # Define the sample datasets
        a = "(VALUES (1, 'A1'), (2, 'A2'), (3, 'A3')) AS a(id, value)"
        b = "(VALUES (2, 'B1'), (3, 'B2'), (4, 'B3')) AS b(id, value)"
        
        if operation in ("INNER JOIN", "LEFT JOIN", "FULL OUTER JOIN"):
            query = f"SELECT a.id, a.value AS value_a, b.value AS value_b FROM {a} {operation} {b} ON a.id = b.id"
        else:
            query = f"SELECT * FROM {a} {operation} SELECT * FROM {b}"
        
        result = spark.sql(query)
        return "Query executed successfully", result.toPandas()
    except Exception as e:
        return f"Error: {str(e)}", None

# Create the Gradio interface
with gr.Blocks(title="Databricks Connect Demo") as demo:
    gr.Markdown("# Compute")
    gr.Markdown("## Connect")
    gr.Markdown("""
    This recipe uses [Databricks Connect](https://docs.databricks.com/en/dev-tools/databricks-connect/python/index.html) 
    to execute pre-defined Python or SQL code on a **shared** cluster with UI inputs.
    """)
    
    cluster_id_input = gr.Textbox(
        label="Specify cluster id",
        placeholder="0709-132523-cnhxf2p6",
        info="Copy a shared Compute cluster ID to connect to."
    )
    
    with gr.Tabs():
        with gr.Tab("Python"):
            num_points = gr.Number(
                label="How many data points to generate?",
                value=10,
                minimum=1,
                step=1
            )
            python_btn = gr.Button("Generate")
            python_output_text = gr.Textbox(label="Connection Info")
            python_output_df = gr.Dataframe(label="Data")
            
            python_btn.click(
                handle_python_compute,
                inputs=[cluster_id_input, num_points],
                outputs=[python_output_text, python_output_df]
            )
        
        with gr.Tab("SQL"):
            # Display sample datasets
            gr.Markdown("### Sample Datasets")
            with gr.Row():
                gr.Dataframe(
                    value=pd.DataFrame({"id": [1, 2, 3], "value": ["A1", "A2", "A3"]}),
                    label="Dataset A"
                )
                gr.Dataframe(
                    value=pd.DataFrame({"id": [2, 3, 4], "value": ["B1", "B2", "B3"]}),
                    label="Dataset B"
                )
            
            operation = gr.Dropdown(
                choices=["INNER JOIN", "LEFT JOIN", "FULL OUTER JOIN", "UNION", "EXCEPT"],
                label="Choose how to handle these data",
                value="INNER JOIN"
            )
            sql_btn = gr.Button("Perform")
            sql_output_text = gr.Textbox(label="Status")
            sql_output_df = gr.Dataframe(label="Output")
            
            sql_btn.click(
                handle_sql_compute,
                inputs=[cluster_id_input, operation],
                outputs=[sql_output_text, sql_output_df]
            )

    with gr.Accordion("Requirements"):
        gr.Markdown("""
        **Permissions (app service principal)**
        * `CAN ATTACH TO` permission on the cluster
        
        **Databricks resources**
        * All-purpose compute
        
        **Dependencies**
        * [Databricks Connect](https://pypi.org/project/databricks-connect/) - `databricks-connect`
        * [Gradio](https://pypi.org/project/gradio/) - `gradio`
        """)

if __name__ == "__main__":
    demo.launch()