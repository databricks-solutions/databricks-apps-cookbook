---
sidebar_position: 2
---

# Deployment instructions

Follow these instructions to deploy the interactive examples to your Databricks workspace or to run them locally.

:::warning

These samples are experimental and meant for demonstration purposes only. They are provided as-is and without formal support by Databricks. Ensure your organization's security, compliance, and operational best practices are applied before deploying them to production.

:::

## Deploy to Databricks

1. Navigate to the [databricks-apps-cookbook](https://github.com/databricks-solutions/databricks-apps-cookbook) GitHub repository and [load it a Databricks Git folder](https://docs.databricks.com/en/repos/index.html) in your Databricks workspace.
1. In your Databricks workspace, switch to **Compute** -> **Apps**.
1. Choose **Create app**.
1. Under **Choose how to start**, select **Custom** and choose **Next**.
1. Provide a name for your app and choose **Create app**.
1. Once your app compute has started, choose **Deploy**.
1. Navigate to your new Git folder and select either the `dash` or `streamlit` folder.
1. Choose **Deploy**.

:::info

Check the Requirements tab of each recipe to understand what [service principal permissions](https://docs.databricks.com/en/dev-tools/databricks-apps/app-development.html#configure-resources), Databricks resources, and Python packages are required to use it.

:::

## Run locally

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the [databricks-apps-cookbook](https://github.com/databricks-solutions/databricks-apps-cookbook) GitHub repository or your fork to your local machine and switch into the `databricks-apps-cookbook` folder:
   ```bash
   git clone https://github.com/databricks-solutions/databricks-apps-cookbook.git
   cd databricks-apps-cookbook
   ```
1. Navigate to the sub-folder for the cookbook framework you want to run (either `dash` or `streamlit`). Create and activate a Python virtual environment in this folder [`venv`](https://docs.python.org/3/library/venv.html). We recommend using separate environments for each framework:
   ```bash
   cd streamlit
   python3 -m venv .venv
   source .venv/bin/activate
   ```
1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
1. Install the [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/index.html) and authenticate with your Databricks workspace using [OAuth U2M](https://docs.databricks.com/en/dev-tools/auth/oauth-u2m.html), for example:
   ```bash
   databricks auth login --host https://my-workspace.cloud.databricks.com/
   ```
1. Set required environment variables:
   ```bash
   export DATABRICKS_HOST=https://my-workspace.cloud.databricks.com/
   ```
1. Run the cookbook app locally (make sure your virtual environment is activated).

   Streamlit:

   ```bash
   streamlit run app.py
   ```

   Dash:

   ```bash
   python app.py
   ```

   FastAPI:

   ```bash
   uvicorn app:app
   ```

:::info

Make sure you have a working network connection to your Databricks workspace. Some samples may only work when running on Databricks Apps and not locally, e.g., retrieving information from HTTP headers to identify users.

:::
