"""Tests for the database connector module using pytest best practices."""

import pandas as pd
import pytest
from services.db.connector import get_connection, query, insert_data, close_connections


@pytest.fixture
def mock_sql(mocker):
    """Mock the databricks sql module."""
    return mocker.patch("services.db.connector.sql")


@pytest.fixture
def mock_cursor(mocker):
    """Create a mock cursor with test data."""
    cursor = mocker.MagicMock()
    cursor.description = [("id",), ("name",)]
    cursor.fetchall.return_value = [(1, "Test")]

    # Add a side effect to set rowcount based on the query type
    def execute_side_effect(query, *args, **kwargs):
        # For INSERT queries, count the number of value tuples
        if "INSERT" in query.upper():
            # Count the number of value tuples in the query
            # Each (?, ?) represents one record being inserted
            value_count = query.count("(?, ?)")
            cursor.rowcount = value_count
        # For SELECT queries, use the fetchall result length
        elif "SELECT" in query.upper():
            cursor.rowcount = len(cursor.fetchall.return_value)
        else:
            cursor.rowcount = 1
        return None

    cursor.execute.side_effect = execute_side_effect

    # Ensure rowcount is properly set before returning
    cursor.rowcount = 0
    return cursor


@pytest.fixture
def mock_connection(mocker, mock_cursor):
    """Create a mock database connection."""
    conn = mocker.MagicMock()
    conn.cursor.return_value.__enter__.return_value = mock_cursor
    return conn


class TestDatabaseConnector:
    """Tests for the database connector functionality."""

    def test_get_connection_creates_proper_connection(self, mocker, mock_sql):
        """Test that get_connection creates a connection with the correct parameters."""
        # Arrange
        warehouse_id = "test-warehouse-id"
        expected_http_path = f"/sql/1.0/warehouses/{warehouse_id}"

        # Act
        get_connection(warehouse_id)

        # Assert
        mock_sql.connect.assert_called_once()
        call_kwargs = mock_sql.connect.call_args.kwargs
        assert call_kwargs["http_path"] == expected_http_path

    def test_query_returns_dict_results(self, mocker, mock_connection, mock_cursor):
        """Test that query returns results as dictionaries when as_dict=True."""
        # Arrange
        test_query = "SELECT * FROM catalog.schema.table"
        mocker.patch(
            "services.db.connector.get_connection", return_value=mock_connection
        )

        # Act
        result = query(test_query, "warehouse-id", as_dict=True)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Test"
        mock_cursor.execute.assert_called_once_with(test_query)

    def test_query_returns_dataframe(self, mocker, mock_connection, mock_cursor):
        """Test that query returns results as a DataFrame when as_dict=False."""
        # Arrange
        test_query = "SELECT * FROM catalog.schema.table"
        mocker.patch(
            "services.db.connector.get_connection", return_value=mock_connection
        )

        # Act
        result = query(test_query, "warehouse-id", as_dict=False)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["id"] == 1
        assert result.iloc[0]["name"] == "Test"
        mock_cursor.execute.assert_called_once_with(test_query)

    def test_query_handles_exceptions(self, mocker):
        """Test that query properly handles and wraps exceptions."""
        # Arrange
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.side_effect = ValueError(
            "Database connection error"
        )
        mocker.patch("services.db.connector.get_connection", return_value=mock_conn)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            query("SELECT 1", "warehouse-id")

        assert "Query failed" in str(exc_info.value)
        assert "Database connection error" in str(exc_info.value)

    def test_close_connections_clears_cache(self, mocker):
        """Test that close_connections clears the connection cache."""
        # Arrange
        mock_cache_clear = mocker.patch.object(get_connection, "cache_clear")

        # Act
        close_connections()

        # Assert
        mock_cache_clear.assert_called_once()


class TestInsertData:
    """Test suite for insert_data function."""

    def test_insert_data_success(self, mocker, mock_connection):
        """Test successful data insertion."""
        # Setup test data
        test_data = [{"id": 1, "name": "Test1"}, {"id": 2, "name": "Test2"}]

        # Patch get_connection to return our mock
        mocker.patch(
            "services.db.connector.get_connection", return_value=mock_connection
        )

        # Call the function
        result = insert_data(
            table_path="test_catalog.test_schema.test_table",
            data=test_data,
            warehouse_id="test-warehouse-123",
        )

        # Assert the result
        assert result == 2  # Number of rows affected

        # Verify the SQL query was built correctly
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.execute.assert_called_once()

        # Get the actual SQL and parameters
        call_args = mock_cursor.execute.call_args[0]
        sql = call_args[0]
        params = call_args[1]

        # Verify SQL structure
        assert "INSERT INTO test_catalog.test_schema.test_table" in sql
        assert "(id, name)" in sql
        assert "VALUES (?, ?), (?, ?)" in sql

        # Verify parameters
        assert params == [1, "Test1", 2, "Test2"]

    def test_insert_data_empty(self, mocker, mock_connection):
        """Test insertion with empty data list."""
        # Call the function with empty data
        mocker.patch(
            "services.db.connector.get_connection", return_value=mock_connection
        )

        result = insert_data(
            table_path="test_catalog.test_schema.test_table",
            data=[],
            warehouse_id="test-warehouse-123",
        )

        # Should return 0 and not execute any query
        assert result == 0
        mock_connection.cursor.assert_not_called()

    def test_insert_data_error(self, mocker, mock_connection):
        """Test error handling during insertion."""
        # Setup mock to raise an exception
        mock_cursor = mock_connection.cursor.return_value.__enter__.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        # Call the function and expect exception
        mocker.patch(
            "services.db.connector.get_connection", return_value=mock_connection
        )

        with pytest.raises(Exception) as exc_info:
            insert_data(
                table_path="test_catalog.test_schema.test_table",
                data=[{"id": 1, "name": "Test"}],
                warehouse_id="test-warehouse-123",
            )

        # Verify error message
        assert "Failed to insert data" in str(exc_info.value)

    def test_insert_data_different_columns(self, mocker, mock_connection):
        """Test insertion with records having different columns."""
        # Setup test data with different columns
        test_data = [
            {"id": 1, "name": "Test1"},
            {"id": 2, "description": "Test2"},  # Different column
        ]

        # Call the function and expect exception
        mocker.patch(
            "services.db.connector.get_connection", return_value=mock_connection
        )

        with pytest.raises(Exception) as exc_info:
            insert_data(
                table_path="test_catalog.test_schema.test_table",
                data=test_data,
                warehouse_id="test-warehouse-123",
            )

        # Verify error message
        assert "Failed to insert data" in str(exc_info.value)
