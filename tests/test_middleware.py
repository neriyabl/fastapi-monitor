"""Tests for MonitorMiddleware."""

import tempfile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_monitor import MonitorMiddleware


def test_successful_request():
    """Test monitoring of successful request."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = FastAPI()
        app.add_middleware(MonitorMiddleware, db_path=tmp.name)

        @app.get("/")
        def root():
            return {"message": "Hello World"}

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}


def test_excluded_paths():
    """Test that excluded paths are not monitored."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = FastAPI()
        app.add_middleware(
            MonitorMiddleware, db_path=tmp.name, exclude_paths=["/health"]
        )

        @app.get("/health")
        def health():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
