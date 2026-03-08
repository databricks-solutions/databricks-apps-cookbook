# Databricks Apps Cookbook - Dash App

An interactive cookbook application that demonstrates common Databricks integration patterns through hands-on "recipes". The app provides a sidebar-navigated, multi-page experience where each recipe page has three tabs: **Try it** (interactive demo), **Code snippet** (implementation reference), and **Requirements** (permissions and resources needed).

## Layout and Navigation

- **Sidebar** (left, ~10% width): Persistent navigation with categorized recipe links grouped into sections (Tables, Volumes, AI/ML, Business Intelligence, Workflows, Compute, Authentication, External Services)
- **Main content area** (right, ~90%): Displays the currently selected recipe page
- **Logo**: Databricks logo displayed at the top of the sidebar

## Pages

### Introduction (Home Page)

**Route:** `/`

The landing page welcomes users and provides an overview of all available recipes.

- Displays a "Databricks Apps Cookbook" header with a welcome message
- Shows recipe cards organized by category in a grid layout, each linking to the corresponding recipe page
- Includes a "Links" section with external resources: official documentation (AWS, Azure, Python SDK), code samples, and blog posts

---

### Read a Delta Table

**Route:** `/tables/read`

Lets users query and view data from a Databricks Delta table.

1. User enters an **HTTP Path** to a SQL warehouse (e.g., `/sql/1.0/warehouses/xxxxxx`)
2. User enters a **Unity Catalog table name** (e.g., `catalog.schema.table`)
3. User clicks **"Load Table"**
4. The app connects to the specified SQL warehouse and runs `SELECT *` on the table
5. Results display in a paginated, sortable data table (10 rows per page)
6. Errors display as a red alert banner

---

### Edit a Delta Table

**Route:** `/tables/edit`

Lets users load, edit, and save changes to a Delta table.

1. User enters the **HTTP Path** and **table name**, then clicks **"Load Table"**
2. Data loads into an editable table where users can click cells to modify values and delete rows
3. A **"Save Changes"** button appears after the table loads
4. Clicking **"Save Changes"** writes the modified data back to the table using an INSERT OVERWRITE operation
5. A success or error message displays after the save attempt

---

### OLTP Database

**Route:** `/oltp-database`

Demonstrates querying a Lakebase (PostgreSQL-compatible) transactional database.

1. User selects a **database instance** from a dropdown (populated from available instances)
2. User enters a **database name** (default: `databricks_postgres`), **schema** (default: `public`), and **table** (default: `app_state`)
3. User clicks **"Query Table"**
4. The app retrieves an OAuth token, connects to the database, and runs `SELECT * FROM schema.table LIMIT 10`
5. Results display in a styled data table
6. Errors display as alert banners (e.g., permission denied, connection failed)

---

### Upload a File to Volumes

**Route:** `/volumes/upload`

Lets users upload files to a Unity Catalog Volume.

1. User enters a **volume path** (e.g., `main.marketing.raw_files`)
2. User clicks **"Check Volume and permissions"** — the app validates the volume exists and the user has WRITE access
3. On success, a file upload area appears (drag-and-drop or file picker)
4. User selects a file and clicks **"Upload file to {volume_path}"**
5. On success, the app shows a confirmation message with a link to the volume in the Databricks UI
6. Errors display as red alerts

---

### Download a File from Volumes

**Route:** `/volumes/download`

Lets users download a file from a Unity Catalog Volume.

1. User enters the **full file path** in the volume (e.g., `/Volumes/main/marketing/raw_files/leads.csv`)
2. User clicks **"Get file"**
3. The app downloads the file and presents a **"Download file"** button that triggers a browser download
4. Errors display as red alerts

---

### Invoke a Model

**Route:** `/ml/serving-invoke`

Lets users invoke a Databricks model serving endpoint.

1. User selects a **model endpoint** from a dropdown (populated from deployed endpoints)
2. User selects **model type**: "LLM" or "Traditional ML"
3. **For LLM**: User adjusts a **temperature slider** (0.0–2.0) and enters a **prompt** in a text area, then clicks **"Invoke LLM"**
4. **For Traditional ML**: User enters a **JSON input** matching the model's expected schema, then clicks **"Invoke ML Model"**
5. The response displays as formatted JSON
6. Errors display as red alerts

---

### Invoke a Multi-Modal LLM

**Route:** `/ml/multimodal`

Lets users send an image and text prompt to a multi-modal language model.

1. User selects a **model** from a dropdown
2. User uploads an **image** (JPG, PNG, JPEG) — a preview displays on the right side
3. User enters a **prompt** in a text area
4. User clicks **"Invoke LLM"**
5. The LLM response displays as formatted markdown text
6. Errors display as red alerts

---

### Run Vector Search

**Route:** `/ml/vector-search`

Lets users perform a similarity search against a Databricks Vector Search index.

1. User enters the **vector search index name** (e.g., `catalog.schema.index-name`)
2. User enters **columns to retrieve** (comma-separated, e.g., `url, name`)
3. User enters a **search query** in natural language (e.g., `What is Databricks?`)
4. User clicks **"Run vector search"**
5. The app generates embeddings from the query, searches the index, and returns the top 3 results
6. Results display in a formatted card
7. Errors display as red alerts

---

### Connect to MCP Server

**Route:** `/ml/mcp-connect`

Lets users send HTTP requests to an external service through a Databricks MCP (Model Context Protocol) connection.

1. User enters a **connection name** (a Unity Catalog connection)
2. User selects an **authentication mode** (bearer token, OAuth user-to-machine, OAuth machine-to-machine)
3. User selects an **HTTP method** (GET or POST)
4. User enters a **JSON request body**
5. User clicks **"Send Request"**
6. On first request, the app initializes an MCP session and displays the session ID
7. The response displays as formatted JSON
8. If login is required (for OAuth flows), a **"Login"** button appears with the authentication URL

---

### Genie (AI/BI Chat)

**Route:** `/bi/genie`

Provides a conversational interface to Databricks Genie for natural-language data queries.

1. User enters a **Genie Space ID**
2. User types a question in the **prompt text area** and clicks **"Ask Genie"**
3. The first message creates a new conversation; subsequent messages continue the same conversation (conversation ID auto-fills)
4. Responses display as chat-style message cards:
   - Text responses rendered as formatted text
   - Query results displayed as data tables
5. User can click **"Clear Chat"** to reset the conversation
6. Errors display as red alerts

---

### Embed AI/BI Dashboard

**Route:** `/bi/dashboard`

Embeds a Databricks Lakeview dashboard inside the app.

1. User enters a **dashboard embed URL** in the input field
2. The dashboard renders in an iframe (100% width, 600px height) below the input
3. If no URL is entered, a placeholder message displays: "Enter a dashboard URL to embed it here."

---

### Trigger a Job

**Route:** `/workflows/run`

Lets users trigger a Databricks workflow job.

1. User enters a **Job ID**
2. User enters **job parameters** as a JSON object (e.g., `{"param1": "value1"}`)
3. User clicks **"Trigger job"**
4. On success, a confirmation message displays with the `run_id` and job state as JSON
5. Errors display as red alerts (e.g., invalid JSON, job not found)

---

### Retrieve Job Results

**Route:** `/workflows/get-results`

Lets users retrieve the output of a completed workflow task.

1. User enters a **Task Run ID**
2. User clicks **"Get task run results"**
3. The app fetches the run output and displays available output types as separate cards:
   - SQL output
   - dbt output
   - Run job output (notebook)
   - Notebook output
4. Each output type displays as formatted JSON
5. Errors display as red alerts

---

### Connect to Compute

**Route:** `/compute/connect`

Demonstrates connecting to a Databricks cluster and running Spark operations.

1. User enters a **Cluster ID** — the app attempts to connect and shows a connection status message
2. Two sub-tabs are available:
   - **Python tab**: User enters a number of **data points** to generate, clicks **"Generate"**, and sees a table of generated range data
   - **SQL tab**: Two sample datasets (A and B) are displayed. User selects a **SQL operation** (INNER JOIN, LEFT JOIN, FULL OUTER JOIN, UNION, EXCEPT) from a dropdown, clicks **"Perform"**, and sees the query result
3. Errors display as red alerts

---

### Get Current User

**Route:** `/users/get-current`

Displays the identity of the currently authenticated user based on HTTP request headers.

- Automatically displays on page load (no user input required):
  - **Email** (from `X-Forwarded-Email` header)
  - **Username** (from `X-Forwarded-Preferred-Username` header)
  - **User** (from `X-Forwarded-User` header)
  - **IP Address** (from `X-Real-Ip` header)
- Shows all HTTP headers as formatted text
- Missing headers show "Not available"

---

### Retrieve a Secret

**Route:** `/secrets/retrieve`

Lets users retrieve a secret from Databricks Secrets.

1. User enters a **secret scope** (e.g., `apis`)
2. User enters a **secret key** (e.g., `weather_service_key`)
3. User clicks **"Retrieve"**
4. On success, a confirmation message displays: "Secret retrieved! The value is securely handled in the backend." (the actual secret value is NOT shown in the UI)
5. On failure, an error message displays: "Secret not found or inaccessible..."

---

### External Connections

**Route:** `/external/connections`

Lets users make HTTP requests to external services through Databricks Unity Catalog connections.

1. User enters a **connection name**
2. User selects an **authentication mode** (bearer token, OAuth user-to-machine, OAuth machine-to-machine)
3. User selects an **HTTP method** (GET or POST)
4. User optionally enters a **request path**, **JSON request body**, and **JSON request headers**
5. User clicks **"Send Request"**
6. The response displays as formatted JSON
7. If OAuth login is required, a **"Login to Connection"** button appears, followed by a **"Retry Request"** button
8. Errors display as red alerts
