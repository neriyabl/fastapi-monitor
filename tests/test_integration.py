"""Integration tests for FastAPI Monitor."""

import tempfile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_monitor import MonitorMiddleware, create_dashboard_app


def test_full_integration():
    """Test complete integration of monitoring and dashboard."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = FastAPI()
        app.add_middleware(MonitorMiddleware, db_path=tmp.name)

        @app.get("/")
        def root():
            return {"message": "Hello World"}

        @app.get("/users/{user_id}")
        def get_user(user_id: int):
            return {"user_id": user_id}

        # Mount dashboard
        dashboard_app = create_dashboard_app(tmp.name)
        app.mount("/monitor", dashboard_app)

        client = TestClient(app)

        # Make some API requests
        response = client.get("/")
        assert response.status_code == 200

        response = client.get("/users/123")
        assert response.status_code == 200

        # Check dashboard is accessible
        response = client.get("/monitor/")
        assert response.status_code == 200

        # Check dashboard API
        response = client.get("/monitor/api/stats")
        assert response.status_code == 200
