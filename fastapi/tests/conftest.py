"""Test configuration for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture(scope="session")
def app_instance():
    """Create an application instance for testing."""
    # Here you could do any app setup that should happen once for all tests
    # For example, set test configurations, initialize test data, etc.
    return app


@pytest.fixture
def client(app_instance):
    """Create a test client for the FastAPI application."""
    with TestClient(app_instance) as test_client:
        # Setup before test - can add authentication or other context
        yield test_client
        # Teardown after test - can clean up resources
