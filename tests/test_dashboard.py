"""Tests for dashboard functionality."""

import tempfile

from fastapi.testclient import TestClient

from fastapi_monitor import create_dashboard_app


def test_dashboard_main_page():
    """Test main dashboard page loads."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


def test_api_stats():
    """Test stats API endpoint."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/api/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_requests" in data
        assert "avg_response_time" in data


def test_api_requests():
    """Test requests API endpoint."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/api/requests")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
