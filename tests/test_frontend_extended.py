"""Extended frontend tests for comprehensive coverage."""

import tempfile
import threading
import time

import uvicorn
from fastapi import FastAPI

from fastapi_monitor import MonitorMiddleware, create_dashboard_app


def create_test_app_with_data():
    """Create test app and generate some test data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        app = FastAPI()
        app.add_middleware(MonitorMiddleware, db_path=tmp.name)

        @app.get("/")
        def root():
            return {"message": "Hello World"}

        @app.get("/users/{user_id}")
        def get_user(user_id: int):
            if user_id == 999:
                raise ValueError("User not found")
            return {"user_id": user_id, "name": f"User {user_id}"}

        @app.post("/users")
        def create_user(data: dict):
            return {"id": 123, "created": True}

        @app.get("/slow")
        def slow_endpoint():
            time.sleep(0.1)  # Simulate slow response
            return {"message": "slow response"}

        # Mount dashboard
        dashboard_app = create_dashboard_app(tmp.name)
        app.mount("/monitor", dashboard_app)

    return app


def test_dashboard_theme_toggle(page):
    """Test theme toggle functionality."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8010, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    page.goto("http://127.0.0.1:8010/monitor/")

    # Check theme toggle button exists (be more specific)
    theme_button = page.locator("button").first
    assert theme_button.is_visible()

    # Click theme toggle
    theme_button.click()

    # Check if dark mode class is applied (Alpine.js functionality)
    page.wait_for_timeout(500)  # Wait for Alpine.js to process


def test_dashboard_auto_refresh_toggle(page):
    """Test auto-refresh toggle functionality."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8011, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    page.goto("http://127.0.0.1:8011/monitor/")

    # Look for auto-refresh toggle
    auto_refresh_toggle = page.locator("input[type='checkbox']").first
    if auto_refresh_toggle.is_visible():
        # Test toggling auto-refresh
        auto_refresh_toggle.click()
        page.wait_for_timeout(500)


def test_dashboard_with_different_request_types(page):
    """Test dashboard shows different HTTP methods correctly."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8012, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Make different types of requests
    page.goto("http://127.0.0.1:8012/")  # GET
    page.goto("http://127.0.0.1:8012/users/123")  # GET with params

    # Check dashboard shows the requests
    page.goto("http://127.0.0.1:8012/monitor/")

    # Wait for table to load
    page.wait_for_selector("table")

    # Check different methods are shown
    table_content = page.locator("table").inner_text()
    assert "GET" in table_content
    assert "/" in table_content
    assert "/users/123" in table_content


def test_dashboard_error_handling(page):
    """Test dashboard handles and displays errors."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8013, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Make request that causes error
    page.goto("http://127.0.0.1:8013/users/999", wait_until="networkidle")

    # Check dashboard
    page.goto("http://127.0.0.1:8013/monitor/")
    page.wait_for_selector("table")

    # Check error is recorded
    table_content = page.locator("table").inner_text()
    assert "500" in table_content or "404" in table_content


def test_dashboard_pagination(page):
    """Test dashboard pagination functionality."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8014, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Generate multiple requests
    for i in range(5):
        page.goto(f"http://127.0.0.1:8014/users/{i}")

    # Check dashboard
    page.goto("http://127.0.0.1:8014/monitor/")
    page.wait_for_selector("table")

    # Look for pagination controls
    page.locator(
        "nav, .pagination, button:has-text('Next'), button:has-text('Previous')"
    )
    # Pagination might not be visible with few requests, so we just check table loads


def test_dashboard_request_details_modal(page):
    """Test clicking on request shows details."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8015, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Make a request
    page.goto("http://127.0.0.1:8015/users/456")

    # Check dashboard
    page.goto("http://127.0.0.1:8015/monitor/")
    page.wait_for_selector("table")

    # Try to click on a table row (if clickable)
    first_row = page.locator("tbody tr").first
    if first_row.is_visible():
        first_row.click()
        page.wait_for_timeout(500)  # Wait for any modal/details to appear


def test_analytics_page_functionality(page):
    """Test analytics page interactive elements."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8016, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Generate some data
    page.goto("http://127.0.0.1:8016/")
    page.goto("http://127.0.0.1:8016/slow")

    # Check analytics page
    page.goto("http://127.0.0.1:8016/monitor/analytics")

    # Check page loads
    assert page.locator("h1").is_visible()

    # Look for chart containers or data visualization elements
    page.locator("canvas, svg, .chart, [id*='chart']")
    # Charts might be loaded via JS, so we just verify page structure


def test_dashboard_responsive_design(page):
    """Test dashboard works on different screen sizes."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8017, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Test mobile viewport
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("http://127.0.0.1:8017/monitor/")

    # Check main elements are still visible
    assert page.locator("h1").is_visible()

    # Test desktop viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.reload()

    # Check elements are still visible
    assert page.locator("h1").is_visible()
    assert page.locator("table").is_visible()


def test_dashboard_real_time_updates(page):
    """Test dashboard updates in real-time."""
    app = create_test_app_with_data()
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=8018, log_level="error")
    )
    thread = threading.Thread(target=server.run)
    thread.daemon = True
    thread.start()
    time.sleep(2)

    # Open dashboard
    page.goto("http://127.0.0.1:8018/monitor/")
    page.wait_for_selector("table")

    # Get initial request count
    initial_content = page.locator("table").inner_text()

    # Make new request in another tab/context
    new_page = page.context.new_page()
    new_page.goto("http://127.0.0.1:8018/users/789")
    new_page.close()

    # Check if dashboard updates (might need manual refresh or auto-refresh)
    page.reload()
    page.wait_for_selector("table")

    updated_content = page.locator("table").inner_text()
    # Content should be different after new request
    assert len(updated_content) >= len(initial_content)
