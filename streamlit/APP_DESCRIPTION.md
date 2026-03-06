# Databricks Apps Cookbook - Streamlit App

An interactive cookbook application that demonstrates common Databricks integration patterns through hands-on "recipes". The app provides a sidebar-navigated, multi-page experience where each recipe page has three tabs: **Try it** (interactive demo), **Code snippet** (implementation reference), and **Requirements** (permissions and resources needed).

## Layout and Navigation

- **Sidebar** (left): Grouped navigation sections with recipe links, organized into 10+ categories
- **Main content area**: Displays the currently selected recipe page
- **Logo**: Databricks logo displayed at the top
- **Title**: "Databricks Apps Cookbook" with emoji icons
- Wide page layout

### Navigation Categories

1. Introduction
2. Tables (Read a Lakebase table, Read a Databricks table, Edit a Databricks table)
3. Volumes (Upload, Download)
4. AI/ML (Invoke Model, Multi-Modal LLM, Vector Search, MCP Connect)
5. Business Intelligence (AI/BI Dashboard, Genie)
6. Workflows (Trigger Job, Retrieve Results)
7. Compute (Connect to Cluster, Connect to Serverless)
8. Unity Catalog (List Catalogs & Schemas)
9. Authentication (Get Current User, On-Behalf-Of User)
10. Visualizations (Charts, Maps)
11. External Services (External Connections, Retrieve Secret)

## Pages

### Introduction (Home Page)

The landing page welcomes users and provides an overview of all available recipes.

- Displays a welcome message with custom CSS styling
- Shows recipe cards in a 4-column grid layout, each card containing a category title with clickable recipe links
- Includes a "Links" section with 3 columns of external resources: official documentation (AWS, Azure, Python SDK), code samples, and blog posts
- Links to the GitHub repository

---

### Read a Delta Table

Lets users query and view data from a Databricks Delta table using cascading dropdown selectors.

1. User selects a **SQL warehouse** from a dropdown (auto-populated from workspace)
2. User selects a **catalog** from a dropdown (auto-populated)
3. User selects a **schema** from a dropdown (populated based on selected catalog)
4. User selects a **table** from a dropdown (populated based on selected schema)
5. Data automatically loads and displays as a DataFrame preview when all selections are made

---

### Edit a Delta Table

Lets users load, interactively edit, and save changes to a Delta table.

1. User selects **warehouse**, **catalog**, **schema**, and **table** using cascading dropdowns
2. Data loads into an interactive data editor with:
   - All columns editable
   - Ability to add and remove rows dynamically
   - Hidden index column
3. If changes are detected, a **"Save changes"** button appears
4. Clicking **"Save changes"** writes modified data back using INSERT OVERWRITE
5. A spinner shows "Calling Databricks SQL..." during save
6. Success message displays on completion

---

### OLTP Database (Lakebase Read)

Demonstrates querying a Lakebase (PostgreSQL-compatible) transactional database.

1. User selects a **database instance** from a dropdown (populated from available instances)
2. User enters a **database name** (default: `databricks_postgres`), **schema** (default: `public`), and **table name**
3. User clicks **"Read table"**
4. The app connects using OAuth, executes `SELECT * FROM schema.table LIMIT 100`
5. Results display as a DataFrame with a caption showing the source table
6. Errors display as error messages

---

### Upload a File to Volumes

Lets users upload files to a Unity Catalog Volume with permission validation.

1. User enters a **volume path** (e.g., `main.marketing.raw_files`)
2. User clicks **"Check Volume and permissions"** (lock icon button)
3. The app validates the volume exists and the user has WRITE_VOLUME privilege
4. On success, a **file uploader widget** appears
5. User selects a file, then clicks **"Upload file to {volume_path}"** (upload icon button)
6. On success, a confirmation message displays with a clickable link to the volume in the Databricks UI
7. Errors display as error messages

---

### Download a File from Volumes

Lets users download a file from a Unity Catalog Volume.

1. User enters the **full file path** in the volume (e.g., `/Volumes/main/marketing/raw_files/leads.csv`)
2. User clicks **"Get file"**
3. On success, a browser **download button** appears with the file ready for download
4. Errors display as error messages

---

### Invoke a Model

Lets users invoke a Databricks model serving endpoint with support for multiple model types.

1. User selects a **model endpoint** from a dropdown (populated from deployed endpoints)
2. User selects **model type**: "LLM" or "Traditional ML"
3. **For LLM**: User adjusts a **temperature slider** (0.0–2.0, step 0.1), enters a **prompt**, and clicks **"Invoke LLM"**
4. **For Traditional ML**: User enters **JSON input** matching the model signature, and clicks **"Invoke Model"**
5. Response displays as JSON
6. The "Code snippets" tab includes expandable sections for 7 different model invocation patterns: Traditional ML (dataframe_split/records), TensorFlow/PyTorch (instances/inputs), Completions, Chat, and Embeddings

---

### Invoke a Multi-Modal LLM

Lets users send an image and text prompt to a multi-modal language model.

1. User selects a **model endpoint** from a dropdown
2. User uploads an **image** (JPG, JPEG, PNG) via file uploader — preview displays with caption
3. User enters a **prompt** (default placeholder: "Describe or ask something about the image...")
4. User clicks **"Invoke LLM"**
5. Response displays as text
6. Conversation history is maintained in session state for multi-turn conversations

---

### Run Vector Search

Lets users perform similarity search against a Databricks Vector Search index.

1. User enters the **vector search index name** (e.g., `catalog.schema.index-name`)
2. User enters **columns to retrieve** (comma-separated)
3. User enters a **search query** in natural language
4. User clicks **"Run vector search"**
5. The app generates embeddings, searches the index, and returns the top 3 results
6. Results display as a data array/DataFrame

---

### Connect to MCP Server

Lets users send HTTP requests through a Databricks MCP connection.

1. User enters a **connection name** (a Unity Catalog connection)
2. User selects an **authentication mode** (bearer token, OAuth user-to-machine, OAuth machine-to-machine)
3. User selects an **HTTP method** (POST, GET, PUT, DELETE, PATCH)
4. User enters a **JSON request body**
5. User clicks **"Send Request"**
6. On first request, the app initializes an MCP session and displays the session ID
7. The response displays as formatted JSON
8. If login is required (for OAuth flows), a **"Login to Connection"** link appears with the authentication URL

---

### AI/BI Dashboard

Embeds a Databricks Lakeview dashboard inside the app.

1. User selects a **dashboard** from a dropdown (auto-populated with published dashboards from the workspace)
2. The selected dashboard renders in an embedded iframe (700×600 pixels, scrolling enabled)
3. If no published dashboards exist, a message indicates none are found
4. A warning note reminds admins to enable dashboard embedding in workspace security settings

---

### Genie (AI/BI Chat)

Provides a conversational interface to Databricks Genie for natural-language data queries.

1. User enters a **Genie Space ID** (Room ID format)
2. User types questions in a **chat input** at the bottom ("Ask your question...")
3. Conversation displays in chat format:
   - **User messages** shown as user chat bubbles
   - **Assistant responses** include:
     - Text content rendered as markdown
     - Data results displayed as DataFrames
     - SQL code shown in expandable "Show generated code" sections
4. **Feedback buttons** (thumbs up/down) allow rating responses
5. **"New Chat"** button resets the conversation
6. **"Open Genie"** link button opens the full Genie UI
7. Errors display as error messages

---

### Trigger a Job

Lets users trigger a Databricks workflow job.

1. User enters a **Job ID** (placeholder: `921773893211960`)
2. User enters **job parameters** as JSON (e.g., `{"param1": "value1"}`)
3. User clicks **"Trigger job"**
4. Validation warnings appear if fields are empty
5. On success, a JSON response displays with `run_id` and job state
6. Errors display if JSON parsing fails or job not found

---

### Retrieve Job Results

Lets users retrieve the output of a completed workflow task.

1. User enters a **Task Run ID**
2. User clicks **"Get task run results"**
3. Success message appears, then output sections display conditionally:
   - SQL output (as JSON)
   - dbt output (as JSON)
   - Run job output / notebook (as JSON)
   - Notebook output (as JSON)
4. Errors display as error messages

---

### Connect to Shared Cluster

Demonstrates connecting to a Databricks cluster and running Spark operations.

1. User enters a **Cluster ID**
2. Session info displays (App Name, Master URL) when connected
3. Two sub-tabs:
   - **Python**: User enters a **number of data points** (min 1, default 10), clicks **"Generate"**, and sees a DataFrame of generated range data
   - **SQL**: Two sample datasets (A and B) are shown. User selects a **SQL operation** (INNER JOIN, LEFT JOIN, FULL OUTER JOIN, UNION, EXCEPT), clicks **"Perform"**, and sees query results as a DataFrame
4. Errors display as error messages

---

### Connect to Serverless Compute

Same functionality as Connect to Shared Cluster, but:

- **No Cluster ID required** — automatically connects to serverless compute
- Same Python and SQL sub-tabs with identical interactive experiences
- Connection is established without user-provided cluster configuration

---

### List Catalogs and Schemas

Lets users browse the Unity Catalog hierarchy.

1. User clicks **"Get catalogs"**
2. A table displays all catalogs with columns: Name, Owner, Comment, Created At, Updated At
3. User selects a **catalog** from a dropdown (populated after catalogs load)
4. User clicks **"Get schemas for selected catalog"**
5. A table displays schemas with columns: Catalog Name, Type, Schema Name, Owner, Comment, Created/Updated timestamps, Predictive Optimization flag, Properties

---

### Get Current User

Displays the identity of the currently authenticated user.

- Automatically displays on page load (no user input required):
  - **Email** (from `X-Forwarded-Email` header)
  - **Username** (from `X-Forwarded-Preferred-Username` header)
  - **IP Address** (from `X-Real-Ip` header)
  - **Access token present** indicator (checkmark or X)
- **"All headers"** section shows the full headers as JSON
- If an access token is present, additional user info from the workspace API displays:
  - User ID, Username, Display Name, Active status, Group count, Entitlement count
- **"Full user object"** section shows the complete user object as JSON
- Info note about on-behalf-of-user authentication

---

### On-Behalf-Of User Authentication

Demonstrates running queries as the logged-in user vs. the app's service principal.

1. User selects a **SQL warehouse**, **catalog**, **schema**, and **table** using cascading dropdowns
2. User selects an **authentication mode**:
   - **"On-behalf-of-user (OBO)"** — uses the logged-in user's token
   - **"Service principal"** — uses the app's own credentials
3. User clicks **"Run query"** (disabled until all fields are selected)
4. The app executes `SELECT * FROM table LIMIT 10` using the chosen auth mode
5. Results display as a DataFrame
6. An info banner explains the difference between OBO and service principal modes

---

### Charts (Visualizations)

Demonstrates interactive data visualizations using NYC taxi trip data.

1. User selects a **SQL warehouse**
2. A **table name** is pre-filled (default: `samples.nyctaxi.trips`)
3. User clicks **"Load Data"**
4. A **data preview** table shows the first 10 rows
5. Five analysis sub-tabs are available:
   - **Demand Patterns**: Bar chart of trips by hour, peak hour metric
   - **Revenue Analysis**: Average fare by hour (line chart), total revenue over time (area chart), best earning hour metric
   - **Trip Characteristics**: Trip distance histogram, trip duration histogram, average distance/duration metrics
   - **Popular Locations**: Top 15 pickup zones (bar chart), top 15 dropoff zones (bar chart)
   - **Time Analysis**: Average trip distance by hour (line chart), average trip duration by hour (line chart)

---

### Map Display and Interaction (Visualizations)

Demonstrates geographic data display and interactive map drawing.

Two sub-tabs:

**Display geo data:**
1. User selects a data source: **"Sample data"** or **"Load from a table"**
2. For sample data: clicking **"Display sample data on map"** shows 10 pre-defined city locations on a map
3. For table data: user selects a **warehouse** and **table name**, sees a data preview, then views latitude/longitude points on an interactive map

**Draw on the map:**
1. User selects an **input type** from a dropdown: Points, Geofences, Polyline, Rectangle, or Circle
2. An interactive map (centered on San Francisco) displays with drawing tools
3. User draws shapes on the map using the enabled tools
4. An expandable section shows the **last active drawing as GeoJSON** (geometry object)

---

### Retrieve a Secret

Lets users retrieve a secret from Databricks Secrets.

1. User enters a **secret scope** (placeholder: `apis`)
2. User enters a **secret key** (placeholder: `weather_service_key`)
3. User clicks **"Retrieve"**
4. On success: "Secret retrieved! The value is securely handled in the backend." (the actual secret value is NOT shown in the UI)
5. On failure: error message about secret not found or inaccessible

---

### External Connections

Lets users make HTTP requests to external services through Databricks Unity Catalog connections.

1. Info banner explains on-behalf-of-user requirement
2. User enters a **connection name**
3. User selects an **authentication mode** (OAuth User to Machine, Bearer token, OAuth Machine to Machine)
4. User selects an **HTTP method** (GET, POST, PUT, DELETE, PATCH)
5. User optionally enters a **path** (e.g., `/api/endpoint`)
6. User optionally enters **request headers** as JSON
7. User optionally enters **request data** as JSON
8. User clicks **"Send Request"**
9. Response displays as JSON
10. If authentication is required, an auth link/button appears
11. Errors display as error messages
