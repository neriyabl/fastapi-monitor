"""Tests for basic authentication."""

import base64
import tempfile

from fastapi.testclient import TestClient

from fastapi_monitor import create_dashboard_app


def test_dashboard_without_auth():
    """Test dashboard works without authentication."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name)
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 200


def test_dashboard_with_auth_no_credentials():
    """Test dashboard with auth requires credentials."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name, username="admin", password="secret")
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 401


def test_dashboard_with_auth_valid_credentials():
    """Test dashboard with valid credentials."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name, username="admin", password="secret")
        client = TestClient(app)

        # Create basic auth header
        credentials = base64.b64encode(b"admin:secret").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}

        response = client.get("/", headers=headers)
        assert response.status_code == 200


def test_dashboard_with_auth_invalid_credentials():
    """Test dashboard with invalid credentials."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name, username="admin", password="secret")
        client = TestClient(app)

        # Create basic auth header with wrong password
        credentials = base64.b64encode(b"admin:wrong").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}

        response = client.get("/", headers=headers)
        assert response.status_code == 401


def test_api_endpoints_with_auth():
    """Test API endpoints require authentication."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = create_dashboard_app(tmp.name, username="admin", password="secret")
        client = TestClient(app)

        credentials = base64.b64encode(b"admin:secret").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}

        # Test all API endpoints
        response = client.get("/api/stats", headers=headers)
        assert response.status_code == 200

        response = client.get("/api/requests", headers=headers)
        assert response.status_code == 200

        response = client.get("/api/analytics", headers=headers)
        assert response.status_code == 200

        # Test without auth
        response = client.get("/api/stats")
        assert response.status_code == 401
