"""
Database connector for Databricks SQL.

This module provides functions to connect to Databricks SQL warehouses
and execute queries against Unity Catalog tables.
"""

from functools import lru_cache
from typing import Dict, List, Optional, Union

import pandas as pd
from databricks import sql
from databricks.sdk.core import Config

# Use Databricks SDK Config for authentication
# In Databricks Apps, auth is handled automatically
cfg = Config()


@lru_cache(maxsize=1)
def get_connection(warehouse_id: str):
    """
    Get or create a connection to the Databricks SQL warehouse.
    Connection is cached using lru_cache to avoid creating multiple connections.

    Args:
        warehouse_id: The ID of the SQL warehouse to connect to

    Returns:
        A connection to the SQL warehouse
    """
    http_path = f"/sql/1.0/warehouses/{warehouse_id}"
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


def close_connections():
    """
    Close all open connections.
    This should be called when shutting down the application.
    """
    # Clear the lru_cache to close connections
    get_connection.cache_clear()


def query(
    sql_query: str, warehouse_id: str, as_dict: bool = True
) -> Union[List[Dict], pd.DataFrame]:
    """
    Execute a query against a Databricks SQL Warehouse.

    Args:
        sql_query: SQL query to execute
        warehouse_id: The ID of the SQL warehouse to connect to
        as_dict: Whether to return results as dictionaries (True) or pandas DataFrame (False)

    Returns:
        Query results as a list of dictionaries or pandas DataFrame

    Raises:
        Exception: If the query fails
    """
    conn = get_connection(warehouse_id)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_query)

            # Use fetchall directly for non-Arrow results
            # and convert to appropriate format
            result = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            if as_dict:
                # Convert to list of dictionaries
                return [dict(zip(columns, row)) for row in result]
            else:
                # Convert to pandas DataFrame
                return pd.DataFrame(result, columns=columns)

    except Exception as e:
        # Don't close the cached connection on error
        raise Exception(f"Query failed: {str(e)}")


def insert_data(table_path: str, data: List[Dict], warehouse_id: str) -> int:
    """
    Insert data into a Databricks Unity Catalog table.

    Args:
        table_path: Full path to the table (catalog.schema.table)
        data: List of dictionaries containing the records to insert
        warehouse_id: The ID of the SQL warehouse to connect to

    Returns:
        Number of records inserted

    Raises:
        Exception: If the insert operation fails
    """
    if not data:
        return 0

    conn = get_connection(warehouse_id)

    try:
        with conn.cursor() as cursor:
            # Get column names from the first record
            columns = list(data[0].keys())
            columns_str = ", ".join(columns)

            # Create placeholders for a single row
            placeholders = ", ".join(["?"] * len(columns))

            # Build the INSERT statement with multiple VALUES clauses
            values_clauses = []
            all_values = []

            for record in data:
                values_clauses.append(f"({placeholders})")
                all_values.extend(record[col] for col in columns)

            insert_query = f"""
                INSERT INTO {table_path} ({columns_str})
                VALUES {", ".join(values_clauses)}
            """

            # Execute the insert with all values in a single statement
            cursor.execute(insert_query, all_values)

            # Get the number of affected rows
            return cursor.rowcount

    except Exception as e:
        raise Exception(f"Failed to insert data: {str(e)}")
