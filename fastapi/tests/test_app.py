"""Tests for the main application."""

import pytest
from fastapi import status


class TestMainApplication:
    """Test suite for the main FastAPI application."""

    def test_root_endpoint_status(self, client):
        """Test the root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_root_endpoint_content(self, client):
        """Test the root endpoint returns the expected content."""
        response = client.get("/")
        data = response.json()

        # Check required fields
        assert "app" in data
        assert "message" in data
        assert "docs" in data

        # Check expected values
        assert data["app"] == "Databricks FastAPI Example"
        assert "Welcome" in data["message"]
        assert data["docs"] == "/docs"

    def test_docs_endpoint(self, client):
        """Test the OpenAPI docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.parametrize(
        "endpoint", ["/not-found", "/api/invalid", "/api/v1/nonexistent"]
    )
    def test_not_found_handling(self, client, endpoint):
        """Test that non-existent endpoints return 404."""
        response = client.get(endpoint)
        assert response.status_code == status.HTTP_404_NOT_FOUND
