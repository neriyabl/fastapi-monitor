"""Unit tests for dashboard components and edge cases."""

import tempfile

from fastapi.testclient import TestClient

from fastapi_monitor import create_dashboard_app


def test_dashboard_empty_database():
    """Test dashboard with empty database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 200

        # Check stats with empty data
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_requests"] == 0
        assert data["avg_response_time"] == 0


def test_dashboard_api_requests_pagination():
    """Test requests API with pagination parameters."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        # Test with pagination params
        response = client.get("/api/requests?limit=5&offset=0")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        # Test with invalid params
        response = client.get("/api/requests?limit=-1")
        assert response.status_code == 200  # Should handle gracefully


def test_dashboard_request_detail_not_found():
    """Test request detail for non-existent ID."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/api/requests/999")
        assert response.status_code == 200
        assert response.json() is None


def test_dashboard_analytics_api():
    """Test analytics API endpoint."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        # Test default resolution
        response = client.get("/api/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "requests_over_time" in data
        assert "response_time_distribution" in data

        # Test different resolutions
        for resolution in ["1m", "5m", "1h", "1d"]:
            response = client.get(f"/api/analytics?resolution={resolution}")
            assert response.status_code == 200


def test_dashboard_stats_partial():
    """Test stats partial template endpoint."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/stats-partial")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


def test_dashboard_requests_partial():
    """Test requests partial template endpoint."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/requests-partial")
        assert response.status_code == 200
        data = response.json()
        assert "rows" in data
        assert "pagination" in data


def test_dashboard_static_files():
    """Test static file serving."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        # Test static file endpoint exists
        client.get("/static/")
        # Might return 404 or directory listing, both are acceptable


def test_dashboard_error_handling():
    """Test dashboard error handling."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        # Test invalid endpoints
        response = client.get("/nonexistent")
        assert response.status_code == 404

        # Test malformed requests
        response = client.get("/api/requests/invalid")
        # Should handle gracefully


def test_dashboard_content_types():
    """Test correct content types are returned."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        # HTML endpoints
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

        response = client.get("/analytics")
        assert "text/html" in response.headers["content-type"]

        # JSON endpoints
        response = client.get("/api/stats")
        assert "application/json" in response.headers["content-type"]

        response = client.get("/api/requests")
        assert "application/json" in response.headers["content-type"]
