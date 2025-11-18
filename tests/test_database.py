"""Tests for MonitorDatabase."""

import tempfile

import pytest

from fastapi_monitor.database import MonitorDatabase


@pytest.mark.asyncio
async def test_store_and_retrieve_request():
    """Test storing and retrieving request data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = MonitorDatabase(tmp.name)
        await db.init_db()

        await db.store_request(
            timestamp=1234567890.0,
            method="GET",
            path="/test",
            query_params="",
            status_code=200,
            response_time=50.0,
        )

        requests = await db.get_recent_requests(limit=1)
        assert len(requests) == 1
        assert requests[0]["method"] == "GET"
        assert requests[0]["path"] == "/test"
        assert requests[0]["status_code"] == 200


@pytest.mark.asyncio
async def test_get_stats():
    """Test getting statistics."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = MonitorDatabase(tmp.name)
        await db.init_db()

        # Add some test data
        await db.store_request(1234567890.0, "GET", "/test1", "", 200, 50.0)
        await db.store_request(1234567891.0, "POST", "/test2", "", 404, 100.0)

        stats = await db.get_stats()
        assert stats["total_requests"] == 2
        assert stats["avg_response_time"] == 75.0
        assert "200" in stats["status_codes"]
        assert "404" in stats["status_codes"]


@pytest.mark.asyncio
async def test_analytics_data():
    """Test getting analytics data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db = MonitorDatabase(tmp.name)
        await db.init_db()

        await db.store_request(1234567890.0, "GET", "/test", "", 200, 50.0)

        analytics = await db.get_analytics_data()
        assert "requests_over_time" in analytics
        assert "response_time_distribution" in analytics
        assert "top_endpoints" in analytics
