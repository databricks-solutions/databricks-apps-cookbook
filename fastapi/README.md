# FastAPI Example for Databricks Apps

This is a sample FastAPI application that demonstrates how API-based applications can be deployed on Databricks Apps runtime.  
The sample application is headless and intended to be used with bearer token authentication (OAuth2).

Please refer to [Databricks authorization methods](https://docs.databricks.com/aws/en/dev-tools/auth/#databricks-authorization-methods) to obtain an OAuth token appropriately.

## API Endpoints

The sample application provides the following API endpoints:

#### API v1
- `/api/v1/healthcheck` - Returns a response to validate the health of the application
- `/api/v1/table` - Query data from Databricks tables
- `/api/v1/orders/count` - Get total order count from PostgreSQL database
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

# Run the application
uvicorn app:app --reload
```

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
- **PostgreSQL Database**: Used for transactional operations and orders management via the `/api/v1/orders/*` endpoints

The PostgreSQL database uses automatic token refresh for Databricks database instances with OAuth authentication.

## Configuration

The application uses environment variables for configuration:

### Databricks SQL Warehouse (for Unity Catalog queries)
- `DATABRICKS_WAREHOUSE_ID` - The ID of the Databricks SQL warehouse
- `DATABRICKS_HOST` - (Optional) The Databricks workspace host
- `DATABRICKS_TOKEN` - (Optional) The Databricks access token

### PostgreSQL Database (for orders management)
- `DATABRICKS_DATABASE_INSTANCE` - The name of the Databricks database instance
- `DATABRICKS_DATABASE_NAME` - The PostgreSQL database name
- `DATABRICKS_DATABASE_PORT` - (Optional) Database port (default: 5432)
- `DEFAULT_POSTGRES_SCHEMA` - (Optional) Database schema (default: public)
- `DEFAULT_POSTGRES_TABLE` - (Optional) Orders table name (default: orders_synced)
- `DB_POOL_SIZE` - (Optional) Connection pool size (default: 5)
- `DB_MAX_OVERFLOW` - (Optional) Max pool overflow (default: 10)
- `DB_POOL_TIMEOUT` - (Optional) Pool timeout in seconds (default: 30)
- `DB_COMMAND_TIMEOUT` - (Optional) Command timeout in seconds (default: 10)
- `DB_POOL_RECYCLE_INTERVAL` - (Optional) Connection recycle interval in seconds (default: 3600)