"""Dashboard FastAPI application."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import MonitorDatabase


def create_dashboard_app(db_path: str = "monitor.db") -> FastAPI:
    """Create dashboard FastAPI application."""
    app = FastAPI(title="FastAPI Monitor Dashboard")

    # Get the package directory
    package_dir = os.path.dirname(__file__)

    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(package_dir, "static")),
        name="static",
    )

    # Templates
    templates = Jinja2Templates(directory=os.path.join(package_dir, "templates"))

    # Database
    db = MonitorDatabase(db_path)

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Main dashboard page."""
        stats = await db.get_stats()

        return templates.TemplateResponse(
            "dashboard.html", {"request": request, "stats": stats}
        )

    @app.get("/api/stats")
    async def get_stats():
        """Get current statistics."""
        return await db.get_stats()

    @app.get("/api/requests")
    async def get_requests(limit: int = 20, offset: int = 0):
        """Get recent requests with pagination."""
        return await db.get_recent_requests(limit, offset)

    @app.get("/api/requests/{request_id}")
    async def get_request_detail(request_id: int):
        """Get detailed request information."""
        return await db.get_request_by_id(request_id)

    @app.get("/stats-partial")
    async def stats_partial(request: Request):
        """Partial template for stats (HTMX)."""
        stats = await db.get_stats()
        return templates.TemplateResponse(
            "partials/stats.html", {"request": request, "stats": stats}
        )

    @app.get("/requests-partial")
    async def requests_partial(request: Request, page: int = 1, limit: int = 20):
        """Partial template for requests table rows (HTMX) with pagination."""
        offset = (page - 1) * limit
        recent_requests = await db.get_recent_requests(limit, offset)

        # Get total count for pagination
        stats = await db.get_stats()
        total_requests = stats["total_requests"]
        total_pages = (total_requests + limit - 1) // limit

        # Return both table rows and pagination as JSON
        rows_html = templates.get_template("partials/requests_rows.html").render(
            {"recent_requests": recent_requests}
        )

        pagination_html = templates.get_template("partials/pagination.html").render(
            {"current_page": page, "total_pages": total_pages, "limit": limit}
        )

        return JSONResponse({"rows": rows_html, "pagination": pagination_html})

    @app.get("/analytics", response_class=HTMLResponse)
    async def analytics(request: Request):
        """Analytics dashboard page."""
        return templates.TemplateResponse("analytics.html", {"request": request})

    @app.get("/api/analytics")
    async def get_analytics(resolution: str = "30s"):
        """Get analytics data for charts."""
        return await db.get_analytics_data(resolution)

    return app
