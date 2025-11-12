"""Tests for the tables module using pure pytest techniques."""

import pytest

from routes.v1.tables import table, insert_table_data
from models.tables import TableInsertRequest
from config.settings import Settings
from errors.exceptions import ConfigurationError, DatabaseError


@pytest.fixture
def mock_settings():
    """Create settings with a test warehouse ID."""
    settings = Settings()
    settings.databricks_warehouse_id = "test-warehouse-123"
    return settings


@pytest.fixture
def mock_settings_no_warehouse():
    """Create settings with no warehouse ID."""
    settings = Settings()
    settings.databricks_warehouse_id = None
    return settings


@pytest.fixture
def mock_query_result():
    """Factory fixture for query results."""

    def _create_data(data=None):
        return data or [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}]

    return _create_data


@pytest.mark.asyncio
class TestTableFunction:
    """Test suite for table function directly."""

    async def test_table_function_success(
        self, mock_settings, mock_query_result, mocker
    ):
        """Test successful table query with valid warehouse ID."""
        # Setup
        test_data = mock_query_result()

        # Create a test function to replace query
        def mock_query(sql_query, warehouse_id, as_dict=True):
            assert "test_catalog.test_schema.test_table" in sql_query
            assert "LIMIT 10 OFFSET 0" in sql_query
            assert warehouse_id == "test-warehouse-123"
            return test_data

        # Apply the monkeypatch
        mocker.patch("routes.v1.tables.query", mock_query)

        # Call function directly
        result = await table(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            limit=10,
            offset=0,
            columns="id,name",
            filter_expr=None,
            settings=mock_settings,
        )

        # Assert result
        assert result.data == test_data
        assert result.count == 2
        assert result.total is None

    async def test_table_function_missing_warehouse(self, mock_settings_no_warehouse):
        """Test function raises error when warehouse ID is missing."""
        # Call function and expect exception
        with pytest.raises(ConfigurationError) as exc_info:
            await table(
                catalog="test_catalog",
                schema="test_schema",
                table="test_table",
                limit=10,
                offset=0,
                columns="*",
                filter_expr=None,
                settings=mock_settings_no_warehouse,
            )

        # Assert exception details
        assert "SQL warehouse ID not configured" in str(exc_info.value)

    async def test_table_function_database_error(self, mock_settings, mocker):
        """Test function handles database errors correctly."""

        # Setup - create a function that raises an exception
        def mock_query_error(*args, **kwargs):
            raise Exception("Database connection failed")

        # Apply the monkeypatch
        mocker.patch("routes.v1.tables.query", mock_query_error)

        # Call function and expect exception
        with pytest.raises(DatabaseError) as exc_info:
            await table(
                catalog="test_catalog",
                schema="test_schema",
                table="test_table",
                limit=10,
                offset=0,
                columns="*",
                filter_expr=None,
                settings=mock_settings,
            )

        # Assert exception details
        assert "Failed to query table" in str(exc_info.value)

    async def test_table_function_with_filter(self, mock_settings, mocker):
        """Test function with filter expression."""
        # Setup - create specific test data for this test
        filter_test_data = [{"id": 6, "timestamp": "2025-04-01"}]

        # Create a test function with assertions
        def mock_query_with_filter(sql_query, warehouse_id, as_dict=True):
            assert "WHERE id > 5 AND timestamp > '2025-04-01'" in sql_query
            assert "LIMIT 20 OFFSET 10" in sql_query
            return filter_test_data

        # Apply the monkeypatch
        mocker.patch("routes.v1.tables.query", mock_query_with_filter)

        # Call function with filter
        result = await table(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            limit=20,
            offset=10,
            columns="id,timestamp",
            filter_expr="id > 5 AND timestamp > '2025-04-01'",
            settings=mock_settings,
        )

        # Assert result
        assert len(result.data) == 1
        assert result.count == 1


@pytest.mark.asyncio
class TestInsertTableData:
    """Test suite for insert_table_data function."""

    async def test_insert_table_data_success(self, mock_settings, mocker):
        """Test successful table data insertion."""
        # Setup test data
        test_data = [{"id": 1, "name": "Test1"}, {"id": 2, "name": "Test2"}]

        # Create a test function to replace insert_data
        def mock_insert_data(table_path, data, warehouse_id):
            assert table_path == "test_catalog.test_schema.test_table"
            assert data == test_data
            assert warehouse_id == "test-warehouse-123"
            # Return the actual number of records inserted
            return len(data)

        # Apply the monkeypatch
        mocker.patch("routes.v1.tables.insert_data", mock_insert_data)

        # Create request object
        request = TableInsertRequest(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            data=test_data,
        )

        # Call the endpoint
        result = await insert_table_data(request, mock_settings)

        # Assert result
        assert result.data == test_data
        assert result.count == 2  # Number of records inserted
        assert result.total == 2  # Should match count for inserts

    async def test_insert_table_data_empty(self, mock_settings, mocker):
        """Test table data insertion with empty data list."""
        # Setup test data
        test_data = []

        # Create a test function to replace insert_data
        def mock_insert_data(table_path, data, warehouse_id):
            assert table_path == "test_catalog.test_schema.test_table"
            assert data == test_data
            assert warehouse_id == "test-warehouse-123"
            return 0  # Return 0 for empty data

        # Apply the monkeypatch
        mocker.patch("routes.v1.tables.insert_data", mock_insert_data)

        # Create request object
        request = TableInsertRequest(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            data=test_data,
        )

        # Call the endpoint
        result = await insert_table_data(request, mock_settings)

        # Assert result
        assert result.data == test_data
        assert result.count == 0
        assert result.total == 0

    async def test_insert_table_data_missing_warehouse(
        self, mock_settings_no_warehouse
    ):
        """Test table data insertion fails when warehouse ID is missing."""
        # Setup test data
        test_data = [{"id": 1, "name": "Test"}]

        # Create request object
        request = TableInsertRequest(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            data=test_data,
        )

        # Call the endpoint and expect exception
        with pytest.raises(ConfigurationError) as exc_info:
            await insert_table_data(request, mock_settings_no_warehouse)

        # Assert exception details
        assert "SQL warehouse ID not configured" in str(exc_info.value)

    async def test_insert_table_data_database_error(self, mock_settings, mocker):
        """Test table data insertion handles database errors correctly."""
        # Setup test data
        test_data = [{"id": 1, "name": "Test"}]

        # Create a function that raises an exception
        def mock_insert_data_error(*args, **kwargs):
            raise Exception("Database connection failed")

        # Apply the monkeypatch
        mocker.patch("routes.v1.tables.insert_data", mock_insert_data_error)

        # Create request object
        request = TableInsertRequest(
            catalog="test_catalog",
            schema="test_schema",
            table="test_table",
            data=test_data,
        )

        # Call the endpoint and expect exception
        with pytest.raises(DatabaseError) as exc_info:
            await insert_table_data(request, mock_settings)

        # Assert exception details
        assert "Failed to insert data" in str(exc_info.value)
