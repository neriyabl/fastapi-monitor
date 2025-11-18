"""Frontend tests using Playwright."""

import tempfile
import threading
import time

import uvicorn
from fastapi import FastAPI

from fastapi_monitor import MonitorMiddleware, create_dashboard_app


def create_test_app():
    """Create test app with monitoring and dashboard."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = FastAPI()
        app.add_middleware(MonitorMiddleware, db_path=tmp.name)

        @app.get("/")
        def root():
            return {"message": "Hello World"}

        @app.get("/api/test")
        def test_endpoint():
            return {"status": "ok", "data": [1, 2, 3]}

        # Mount dashboard
        dashboard_app = create_dashboard_app(tmp.name)
        app.mount("/monitor", dashboard_app)

    return app


def test_dashboard_loads(page):
    """Test that dashboard page loads correctly."""
    # Start test server
    app = create_test_app()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)  # Wait for server to start

    # Test dashboard
    page.goto("http://127.0.0.1:8001/monitor/")

    # Check page loads and has expected content
    assert "FastAPI Monitor Dashboard" in page.title()
    assert page.locator("h1").inner_text() == "FastAPI Monitor Dashboard"

    # Check stats section exists (using more flexible text matching)
    assert page.locator("text=Total Requests").is_visible()
    assert page.locator("text=Avg Response Time").is_visible()


def test_dashboard_shows_requests_table(page):
    """Test that dashboard shows requests table."""
    # Start test server
    app = create_test_app()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8002, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Make API request to generate data
    page.goto("http://127.0.0.1:8002/api/test")

    # Check dashboard
    page.goto("http://127.0.0.1:8002/monitor/")

    # Wait for table to load
    page.wait_for_selector("table", timeout=5000)

    # Check table exists and has headers
    assert page.locator("table").is_visible()
    assert page.locator("th:has-text('Method')").is_visible()
    assert page.locator("th:has-text('Path')").is_visible()
    assert page.locator("th:has-text('Status')").is_visible()


def test_analytics_page_loads(page):
    """Test that analytics page loads."""
    # Start test server
    app = create_test_app()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8003, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Test analytics page
    page.goto("http://127.0.0.1:8003/monitor/analytics")

    # Check page loads
    assert page.locator("h1").is_visible()
    assert "Analytics" in page.content()
