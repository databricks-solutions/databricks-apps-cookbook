"""Tests for the healthcheck endpoint."""

import re
from datetime import datetime
import pytest
from fastapi import status


class TestHealthcheckEndpoint:
    """Test suite for the healthcheck endpoint."""

    def test_healthcheck_status_code(self, client):
        """Test the healthcheck endpoint returns 200 OK."""
        response = client.get("/api/v1/healthcheck")
        assert response.status_code == status.HTTP_200_OK

    def test_healthcheck_content(self, client):
        """Test the healthcheck endpoint returns the expected content."""
        response = client.get("/api/v1/healthcheck")
        data = response.json()

        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "OK"

        # Verify timestamp is in ISO format
        timestamp = data["timestamp"]
        assert timestamp is not None

        # Validate ISO format with regex
        iso_pattern = (
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
        )
        assert re.match(
            iso_pattern, timestamp
        ), f"Timestamp '{timestamp}' is not in ISO format"

        # Ensure timestamp can be parsed
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Could not parse timestamp: {timestamp}")

    @pytest.mark.parametrize(
        "accept_header", ["application/json", "application/json; charset=utf-8"]
    )
    def test_healthcheck_content_type(self, client, accept_header):
        """Test the healthcheck endpoint handles different accept headers."""
        response = client.get("/api/v1/healthcheck", headers={"Accept": accept_header})
        assert response.status_code == status.HTTP_200_OK
        assert "application/json" in response.headers["content-type"]
