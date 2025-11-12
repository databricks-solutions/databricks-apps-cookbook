# FastAPI Example for Databricks Apps

This is a sample FastAPI application that demonstrates how API-based applications can be deployed on Databricks Apps runtime.  
The sample application is headless and intended to be used with bearer token authentication (OAuth2).

Please refer to [Databricks authorization methods](https://docs.databricks.com/aws/en/dev-tools/auth/#databricks-authorization-methods) to obtain an OAuth token appropriately.

## API Endpoints

The sample application provides the following API endpoints:

#### API v1
- `/api/v1/healthcheck` - Returns a response to validate the health of the application
- `/api/v1/table` - Query data from Databricks tables
- `/api/v1/resources/create-lakebase-resources` - Create Lakebase resources
- `/api/v1/resources/delete-lakebase-resources` - Delete Lakebase resources
- `/api/v1/orders/count` - Get total order count from Lakebase (PostgreSQL) database
- `/api/v1/orders/sample` - Get sample order keys for testing
- `/api/v1/orders/pages` - Get orders with traditional page-based pagination
- `/api/v1/orders/stream` - Get orders with cursor-based pagination (recommended for large datasets)
- `/api/v1/orders/{order_key}` - Get a specific order by its key
- `/api/v1/orders/{order_key}/status` - Update order status

#### Documentation
- `/docs` - Interactive OpenAPI documentation

## Running Locally

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies within active venv
pip install -r requirements.txt

# Set environment variables (if not using .env file)
export DATABRICKS_WAREHOUSE_ID=your-warehouse-id

# If using a .env file: 
cp .env.example .env 
# Fill in .env fields

# Run the application
uvicorn app:app --reload
```

## Running the Lakebase Example

❗️**Important**: Following these steps will deploy a Lakebase instance and synced table pipeline in your Databricks workspace that will incur costs.

### 1. Create Lakebase Resources
With the app running and your `.env` file configured:
1. Navigate to http://localhost:8000/docs (Swagger UI)
2. Find the `/api/v1/resources/create-lakebase-resources` endpoint
3. Click **Try it out**
4. Set `create_resources` to `true` (confirming you understand the costs)
5. Configure other fields as needed
6. Click **Execute**
7. Wait for resource creation (takes several minutes)

### 2. Validate and Test
Once resources are created:
1. Check the Databricks UI for: database instance, database, catalog, and `orders_synced` table
2. Restart your local app: `uvicorn app:app --reload`
3. Return to http://localhost:8000/docs - you should now see the `/orders` endpoints available

### 3. Clean Up Resources
To avoid ongoing costs:
1. Navigate to `/api/v1/resources/delete-lakebase-resources` endpoint
2. Set `confirm_deletion` to `true`
3. Click **Execute**

    

## Running Tests

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/v1/test_healthcheck.py
```

## Database Architecture

This application uses a dual database architecture:

- **Databricks SQL Warehouse**: Used for Unity Catalog table queries and analytics workloads via the `/api/v1/table` endpoint
- **Lakebase PostgreSQL Database**: Used for transactional operations and orders management via the `/api/v1/orders/*` endpoints

The Lakebase PostgreSQL database uses automatic token refresh for Databricks database instances with OAuth authentication.

## Configuration

The application uses environment variables for configuration:

### Databricks SQL Warehouse (for Unity Catalog queries)
- `DATABRICKS_WAREHOUSE_ID` - The ID of the Databricks SQL warehouse
- `DATABRICKS_HOST` - (Optional) The Databricks workspace host
- `DATABRICKS_TOKEN` - (Optional) The Databricks access token

### Lakebase PostgreSQL Database (for orders management)
- `LAKEBASE_INSTANCE_NAME` - The name of an existing Databricks database instance or the name of a new instance
- `LAKEBASE_DATABASE_NAME` - The Lakebase PostgreSQL database name
- `LAKEBASE_CATALOG_NAME` - The name of the Lakebase catalog
- `SYNCHED_TABLE_STORAGE_CATALOG` - Catalog where you have permissions to create tables. Used to store metadata from the lakebase synced table pipeline.
- `SYNCHED_TABLE_STORAGE_SCHEMA` - Schema where you have permissions to create tables. Used to store metadata from the lakebase synced table pipeline.
- `DATABRICKS_DATABASE_PORT` - (Optional) Database port (default: 5432)
- `DB_POOL_SIZE` - (Optional) Connection pool size (default: 5)
- `DB_MAX_OVERFLOW` - (Optional) Max pool overflow (default: 10)
- `DB_POOL_TIMEOUT` - (Optional) Pool timeout in seconds (default: 10)
- `DB_COMMAND_TIMEOUT` - (Optional) Command timeout in seconds (default: 30)
- `DB_POOL_RECYCLE_INTERVAL` - (Optional) Connection recycle interval in seconds (default: 3600)