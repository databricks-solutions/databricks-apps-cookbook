# Databricks Apps Cookbook - Reflex App

An interactive cookbook application that demonstrates common Databricks integration patterns through hands-on "recipes". The app provides a sidebar-navigated, multi-page experience where each recipe page has three tabs: **Try It** (interactive demo), **Code Snippet** (implementation reference), and **Requirements/Details** (permissions and resources needed).

## Layout and Navigation

- **Sidebar** (left, hidden on mobile): Displays the Databricks logo and a collapsible navigation menu organized by category
- **Header**: Shows "Databricks Apps Cookbook" title
- **Main content area** (right): Scrollable page content with padding
- **Theme**: Light mode with blue primary color, gray secondary elements, rounded corners, subtle shadows

### Navigation Categories

1. Tables (OLTP Database, Read Delta Table, Edit Delta Table)
2. Volumes (Upload File, Download File)
3. AI/ML (Invoke Model, Vector Search, Connect MCP Server, Multimodal LLM)
4. Business Intelligence (AI/BI Dashboard, Genie)
5. Workflows (Trigger Job, Retrieve Job Results)
6. Compute (Connect Cluster)
7. Unity Catalog (List Catalogs & Schemas)
8. Authentication (Get Current User, On-Behalf-Of User)
9. External Services (External Connections, Retrieve a Secret)

## Pages

### Introduction

**Route:** `/` and `/introduction`

The landing page welcomes users and provides an overview of all available recipes.

- Displays a "Welcome to the Databricks Apps Cookbook!" header with a welcome message
- Shows recipe categories in a 4-column grid layout, each with clickable recipe links
- Includes links to external resources: Databricks documentation, blog posts, and GitHub templates
- Links to the GitHub repository for raising PRs

---

### Read Delta Table

**Route:** `/read-delta-table`

Lets users query and view data from a Databricks Delta table using cascading dropdown selectors.

1. User selects a **SQL Warehouse** from a dropdown (auto-populated)
2. User selects a **Catalog** from a dropdown (auto-populated)
3. User selects a **Schema** from a dropdown (populated based on selected catalog)
4. User selects a **Table** from a dropdown (populated based on selected schema)
5. Data automatically loads and displays in a read-only data editor (60vh height)
6. A loading spinner shows during data fetch
7. Errors display as alert messages

---

### Edit Delta Table

**Route:** `/edit-delta-table`

Lets users load, edit cell values, and save changes to a Delta table.

1. User selects **warehouse**, **catalog**, **schema**, and **table** using cascading dropdowns
2. Data loads into an editable data editor (60vh height)
3. User clicks individual cells to modify values
4. A **"Save Changes"** button appears (disabled if no changes have been made)
5. Clicking **"Save Changes"** writes modified data back using INSERT OVERWRITE
6. A loading spinner shows during save
7. A toast notification confirms success
8. Errors display as alert messages

---

### OLTP Database

**Route:** `/oltp-database`

Demonstrates querying a Lakebase (PostgreSQL-compatible) transactional database with automatic OAuth token management.

1. User enters an **Instance Name** (default: `dbase_instance`), **Database** (default: `databricks_postgres`), **Schema** (default: `public`), and **Table** (default: `app_state`)
2. On page load, the app automatically:
   - Creates a unique session ID
   - Generates a rotating OAuth token
   - Creates a connection pool with automatic token refresh
   - Creates the `app_state` table if it doesn't exist
   - Inserts a session record
3. User clicks **"Run a query"**
4. Results display in a read-only data editor (60vh height)
5. If the query returns no data, a message confirms the table is ready but empty
6. An info note explains that OAuth tokens are valid for 60 minutes with auto-refresh
7. Errors display as alert messages

---

### Upload File

**Route:** `/upload-file`

Lets users upload files to a Unity Catalog Volume with permission validation.

1. User enters a **volume path** (e.g., `main.marketing.raw_files`)
2. User clicks **"Check Volume and permissions"**
3. The app validates the volume exists and the user has WRITE_VOLUME privilege
4. On success, a **file upload area** appears (drag-and-drop or click to select; supports multiple files)
5. Selected files are listed by name
6. An **"Upload"** button appears when files are selected
7. Clicking upload sends each file to the volume with overwrite enabled
8. Toast notifications confirm each file upload
9. Errors display as alert messages

---

### Download File

**Route:** `/download-file`

Lets users download a file from a Unity Catalog Volume.

1. User enters the **full file path** in the volume (e.g., `/Volumes/catalog/schema/volume_name/file.csv`)
2. User clicks **"Download"**
3. The browser's native download dialog appears with the file
4. Errors display as alert messages

---

### Invoke Model

**Route:** `/invoke-model`

Lets users invoke a Databricks model serving endpoint.

1. On page load, the **model endpoint dropdown** is populated from deployed endpoints
2. User selects a model type: **"LLM"** or **"Traditional ML"**
3. **For LLM**:
   - User enters a **prompt** in a text area
   - User adjusts a **temperature slider** (0.0–2.0)
   - User clicks **"Invoke LLM"**
4. **For Traditional ML**:
   - User enters **JSON input** matching the model's expected schema
   - User clicks **"Invoke Model"**
5. Response displays as JSON in a code block
6. The button shows a loading state during the request
7. Errors display as alert messages

---

### Invoke Multi-Modal LLM

**Route:** `/invoke-multimodal-llm`

Lets users send an image and text prompt to a multi-modal language model.

1. On page load, the **model dropdown** is populated from serving endpoints
2. User enters or modifies a **prompt** (pre-filled: "Describe this image")
3. User selects an **image** (JPG, JPEG, PNG) via drag-and-drop or file picker
4. User clicks **"Upload Selected Image"** — a preview displays (max 256px height)
5. User clicks **"Invoke LLM"**
6. A loading spinner shows "Processing..."
7. The LLM response displays as formatted markdown
8. Errors display as alert messages

---

### Run Vector Search

**Route:** `/run-vector-search`

Lets users perform similarity search against a Databricks Vector Search index.

1. User enters the **vector search index name** (e.g., `catalog.schema.index_name`)
2. User enters **columns to retrieve** (comma-separated)
3. User enters a **search query** in natural language
4. User clicks **"Run Vector Search"**
5. The app generates embeddings from the query, searches the index, and returns the top 3 results
6. Results display as JSON in a code block
7. Errors display as alert messages

---

### Connect to MCP Server

**Route:** `/connect-mcp-server`

Lets users send HTTP requests through a Databricks MCP connection.

1. An info box notes this only works when deployed with on-behalf-of-user auth
2. User enters a **Connection Name**
3. User selects an **Auth Mode** (OAuth User to Machine Per User, Bearer token, OAuth Machine to Machine)
4. User selects an **HTTP Method** (POST, GET, PUT, DELETE, PATCH)
5. User enters **Request Data** as JSON
6. User clicks **"Send Request"**
7. If an MCP session is active, the **session ID** displays in a green box
8. Response displays as JSON in a code block
9. If authentication is required, an **"Authenticate with Connection Provider"** link appears
10. Expandable code example accordions show implementation patterns for different auth modes

---

### Genie (AI/BI Chat)

**Route:** `/genie`

Provides a conversational interface to Databricks Genie for natural-language data queries.

1. User enters a **Genie Space ID** (with help text explaining where to find it in the URL)
2. User types a message in the **input text area** and presses Enter or clicks the **send button**
3. Conversation displays in a scrollable chat area (500px height):
   - **User messages**: Blue, right-aligned
   - **Assistant messages**: Gray, left-aligned, containing:
     - Text responses
     - Expandable SQL code blocks (accordion)
     - Query result tables with pagination, search, and sort controls
4. A **"New Chat"** button appears after conversation starts (resets the conversation)
5. An **"Open Genie"** link opens the conversation in the native Genie UI
6. Errors display as alert messages

---

### AI/BI Dashboard

**Route:** `/ai-bi-dashboard`

Embeds a Databricks Lakeview dashboard inside the app.

1. On page load, published dashboards are fetched and populate a **dropdown selector**
2. The default selection is the first published dashboard
3. The selected dashboard renders in an embedded **iframe** (800px height)
4. If no published dashboards exist, a "No published dashboards found" message displays
5. An info warning reminds admins to enable dashboard embedding in workspace security settings
6. Users can interact with the embedded dashboard (filters, drilldowns, etc.)
7. Errors display as alert messages

---

### Trigger Job

**Route:** `/trigger-job`

Lets users trigger a Databricks workflow job.

1. User enters a **Job ID**
2. User enters **job parameters** as JSON (optional)
3. User clicks **"Trigger job"**
4. Validates that Job ID is provided
5. Parses JSON parameters
6. On success, a green box displays the `run_id`
7. Toast notifications confirm success or report errors
8. Errors display in a red alert box (e.g., invalid JSON, job not found)

---

### Retrieve Job Results

**Route:** `/retrieve-job-results`

Lets users retrieve the output of completed workflow tasks.

1. User enters a **Task Run ID**
2. User clicks **"Get task run results"**
3. The app fetches the run, iterates through tasks, and retrieves output for each
4. Output sections display conditionally as JSON code blocks:
   - SQL output
   - dbt output
   - Run job output
   - Notebook output
5. Errors display as alert messages

---

### List Catalogs and Schemas

**Route:** `/list-catalogs-schemas`

Lets users browse the Unity Catalog hierarchy.

1. User clicks **"Get catalogs"**
2. A read-only data editor (256px height) displays catalogs with columns: Name, Owner, Comment, Created At
3. User selects a **catalog** from a dropdown (populated after catalogs load)
4. User clicks **"Get schemas for selected catalog"** (disabled until a catalog is selected)
5. A read-only data editor displays schemas with columns: Name, Owner, Comment
6. If no schemas are loaded, a "No schemas loaded" message displays
7. Errors display as alert messages

---

### Get Current User

**Route:** `/get-current-user`

Displays the identity of the currently authenticated user.

1. User clicks **"Get User Headers"**
2. An info box explains local development requirements
3. Extracted HTTP header information displays:
   - **Email**
   - **Username**
   - **IP Address**
   - **Access token present** (checkmark or X indicator)
4. An expandable **"All headers"** accordion shows the full headers as JSON
5. If an access token is present, additional workspace user info displays:
   - User ID, Username, Display Name, Active status, Groups count, Entitlements count
6. An expandable **"Full user object"** accordion shows the complete user object as JSON
7. Errors display as alert messages

---

### On-Behalf-Of User Authentication

**Route:** `/on-behalf-of-user`

Demonstrates running queries as the logged-in user vs. the app's service principal.

1. An info box explains the difference between OBO and service principal modes
2. On page load, **warehouse** and **catalog** dropdowns populate automatically
3. User selects **warehouse**, **catalog**, **schema**, and **table** using cascading dropdowns
4. User selects an **authentication mode**:
   - **"On-behalf-of-user (OBO)"** — uses the logged-in user's token
   - **"Service principal"** — uses the app's own credentials
5. User clicks **"Run Query (Limit 100)"**
6. A loading spinner shows "Running query..."
7. Results display in a read-only data editor (384px height)
8. Errors display as alert messages

---

### Connect Cluster

**Route:** `/connect-cluster`

Demonstrates connecting to a Databricks cluster and running Spark operations.

1. User enters a **Cluster ID** (with help text: "Copy a shared Compute cluster ID to connect to")
2. User clicks **"Connect and Run"**
3. A loading spinner shows during connection
4. On success, a green checkmark message confirms connection
5. Three output sections display:
   - **Session Info**: Spark configuration details as a code block
   - **SQL Output**: Results of a test SQL query in a read-only data editor
   - **Range Output**: Results of `spark.range(10)` in a read-only data editor
6. Errors display in a red alert box

---

### Retrieve a Secret

**Route:** `/retrieve-a-secret`

Lets users retrieve a secret from Databricks Secrets.

1. User enters a **Secret Scope** (e.g., `apis`)
2. User enters a **Secret Key** (e.g., `weather_service_key`)
3. User clicks **"Retrieve"**
4. On success, a green box displays: "Secret retrieved! The value is securely handled in the backend." (the actual secret value is NOT shown in the UI)
5. On failure, a red box displays: "Secret not found or inaccessible..."

---

### External Connections

**Route:** `/external-connections`

Lets users make HTTP requests to external services through Databricks Unity Catalog connections.

1. An info box explains deployment requirements
2. User enters a **Connection Name**
3. User selects an **Auth Mode** (OAuth User to Machine, Bearer token, OAuth Machine to Machine)
4. User selects an **HTTP Method** (GET, POST, PUT, DELETE, PATCH)
5. User enters a **Path** (e.g., `/api/endpoint`)
6. User optionally enters **request headers** as JSON
7. User optionally enters **request data** as JSON
8. User clicks **"Send Request"**
9. Response displays as JSON in a code block
10. If authentication is required, an auth link appears
11. Expandable code example accordions show implementation patterns
12. Errors display as alert messages
