# Databricks Apps Cookbook - FastAPI App

A headless REST API application that demonstrates backend integration patterns with Databricks. The API uses bearer token authentication and provides endpoints for querying Unity Catalog tables, managing a Lakebase (PostgreSQL-compatible) transactional database, and performing CRUD operations on an orders dataset. The app features automatic API documentation at `/docs`.

## Architecture

The app uses a dual-database architecture:

1. **Databricks SQL Warehouse** — for querying Unity Catalog tables (analytical queries)
2. **Lakebase PostgreSQL Database** — for transactional CRUD operations on orders data

Endpoints that depend on the Lakebase database are conditionally registered — they only become available if the database instance exists. This allows the app to run in a limited mode (healthcheck + table queries only) when Lakebase resources haven't been provisioned.

The app automatically refreshes OAuth tokens for persistent database connections (every 50 minutes), runs background health checks (every 300 seconds), and tracks request performance via response headers.

## API Endpoints

### Root

**`GET /`**

Returns a welcome message with basic app information and a link to the API docs.

Response:
- App name
- Welcome message
- Link to `/docs`

---

### Health Check

**`GET /api/v1/healthcheck`**

Returns the API health status with a current timestamp. Used for monitoring and availability checks.

---

### Query a Unity Catalog Table

**`GET /api/v1/table`**

Queries data from any Unity Catalog table through the SQL warehouse.

**Inputs (query parameters):**
- `catalog` (required): Catalog name
- `schema` (required): Schema name
- `table` (required): Table name
- `limit` (optional, default 100, max 1000): Maximum rows to return
- `offset` (optional, default 0): Rows to skip for pagination
- `columns` (optional, default `*`): Comma-separated list of columns to select
- `filter_expr` (optional): SQL WHERE clause (without the `WHERE` keyword)

**Response:** Array of row objects with row count.

**User journey:** Analytics and reporting consumers query data from Unity Catalog with filtering and pagination support.

---

### Insert Data into a Unity Catalog Table

**`POST /api/v1/table`**

Inserts records into a Unity Catalog table.

**Inputs (JSON body):**
- `catalog`: Catalog name
- `schema`: Schema name
- `table`: Table name
- `data`: Array of row objects to insert

**Response:** The inserted data with record count.

**User journey:** Data ingestion workflow — applications push batch data into Unity Catalog tables.

---

### Create Lakebase Resources

**`POST /api/v1/resources/create-lakebase-resources`**

Provisions all necessary Lakebase infrastructure for the orders demo.

**Inputs (query parameters):**
- `create_resources` (required, must be `true`): Explicit cost confirmation
- `capacity` (optional, default `CU_1`): Instance capacity tier
- `node_count` (optional, default 1): Number of nodes
- `enable_readable_secondaries` (optional, default false): Enable read replicas
- `retention_window_in_days` (optional, default 7): Backup retention period

**What gets created:**
1. A Databricks database instance (PostgreSQL-based)
2. A database catalog connecting to the instance
3. A synced table pipeline that mirrors `samples.tpch.orders` into the database
4. A superuser database role for the current user

**Response:** Instance name, catalog name, pipeline ID, and a link to monitor pipeline progress.

**User journey:**
1. Developer confirms cost understanding by setting `create_resources=true`
2. Resources deploy asynchronously (takes several minutes)
3. Developer monitors pipeline progress via the returned Databricks UI link
4. Once provisioning completes, the app must be restarted to activate the orders endpoints

---

### Delete Lakebase Resources

**`DELETE /api/v1/resources/delete-lakebase-resources`**

Removes all Lakebase resources (synced table, catalog, database instance).

**Inputs (query parameters):**
- `confirm_deletion` (required, must be `true`): Safety confirmation

**Response:** List of successfully deleted resources, any failed deletions, and a summary message.

**User journey:** Cleanup workflow — developers remove expensive resources when done testing.

---

### Get Order Count

**`GET /api/v1/orders/count`**

Returns the total number of orders in the Lakebase database.

**Response:** `{ "total_orders": <number> }`

**User journey:** Quick metadata check — users learn dataset size before browsing.

---

### Get Sample Order Keys

**`GET /api/v1/orders/sample`**

Returns the first 5 order keys for testing and discovery.

**Response:** `{ "sample_order_keys": [1, 2, 3, 4, 5] }`

**User journey:** Testing workflow — developers discover valid order keys to use with other endpoints.

---

### Get Orders (Page-Based Pagination)

**`GET /api/v1/orders/pages`**

Retrieves orders using traditional page-based pagination.

**Inputs (query parameters):**
- `page` (optional, default 1): Page number (1-based)
- `page_size` (optional, default 100, max 1000): Records per page
- `include_count` (optional, default true): Whether to calculate total count (can be expensive for large datasets)

**Response:** Array of order objects plus pagination metadata:
- `page`, `page_size`, `total_pages`, `total_count`
- `has_next`, `has_previous`
- `next_cursor`, `previous_cursor` (cursor hints for switching to cursor-based pagination)

**User journey:** Traditional UI pagination — users browse pages by number (page 1, 2, 3...). Best for small-to-medium datasets where users jump to specific pages.

---

### Get Orders (Cursor-Based Pagination)

**`GET /api/v1/orders/stream`**

Retrieves orders using cursor-based pagination for efficient streaming.

**Inputs (query parameters):**
- `cursor` (optional, default 0): Start after this order key (0 = from beginning)
- `page_size` (optional, default 100, max 1000): Records to fetch

**Response:** Array of order objects plus pagination metadata:
- `page_size`, `has_next`, `has_previous`
- `next_cursor`, `previous_cursor`

**User journey:** Modern infinite scroll UI — clients request successive pages using the `next_cursor` from each response. Best for large datasets (millions of records), high-performance requirements, and real-time feeds.

---

### Get Single Order

**`GET /api/v1/orders/{order_key}`**

Retrieves a single order by its primary key.

**Inputs (path parameter):**
- `order_key`: Integer order key (must be > 0)

**Response:** Full order object with fields: order key, customer key, order status, total price, order date, order priority, clerk, ship priority, and comment.

**Error responses:**
- 400 if order key is invalid (≤ 0)
- 404 if order not found

**User journey:** Order detail view — users retrieve specific order information.

---

### Update Order Status

**`POST /api/v1/orders/{order_key}/status`**

Updates the status of a specific order.

**Inputs:**
- Path parameter: `order_key` (must be > 0)
- JSON body: `{ "o_orderstatus": "<new_status>" }`

**Response:** Updated order key, new status, and confirmation message.

**Error responses:**
- 400 if order key is invalid
- 404 if order not found

**User journey:** Order fulfillment workflow — users transition orders through status states.

---

## End-to-End User Journeys

### Journey 1: Analytics Consumer
1. Verify API is running: `GET /api/v1/healthcheck`
2. Query table data: `GET /api/v1/table?catalog=X&schema=Y&table=Z`
3. Paginate with `limit` and `offset`
4. Filter with `filter_expr`

### Journey 2: Setting Up the Lakebase Demo
1. Create resources: `POST /api/v1/resources/create-lakebase-resources?create_resources=true`
2. Wait for async provisioning to complete (monitor via returned pipeline URL)
3. Restart the application
4. Orders endpoints become available
5. Get sample keys: `GET /api/v1/orders/sample`
6. Browse orders with pagination

### Journey 3: Orders Management
1. Check dataset size: `GET /api/v1/orders/count`
2. Browse with page-based pagination: `GET /api/v1/orders/pages?page=1`
3. Or use cursor-based streaming: `GET /api/v1/orders/stream?cursor=0`
4. View order detail: `GET /api/v1/orders/{order_key}`
5. Update order status: `POST /api/v1/orders/{order_key}/status`

### Journey 4: Data Ingestion
1. Prepare batch of records
2. Insert: `POST /api/v1/table` with catalog, schema, table, and data array
3. Receive confirmation with row count

### Journey 5: Resource Cleanup
1. Delete resources: `DELETE /api/v1/resources/delete-lakebase-resources?confirm_deletion=true`
2. Resources removed; app continues in limited mode
