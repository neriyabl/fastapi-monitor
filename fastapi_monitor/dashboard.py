"""Dashboard FastAPI application."""

import os
from typing import Optional

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .auth import create_auth_dependency, no_auth
from .database import MonitorDatabase


def create_dashboard_app(
    db_path: str = "monitor.db",
    username: Optional[str] = None,
    password: Optional[str] = None,
    theme_mode: str = "light",
    color_scheme: str = "default",
) -> FastAPI:
    """Create dashboard FastAPI application with optional basic auth and theme configuration."""
    app = FastAPI(title="FastAPI Monitor Dashboard")

    # Validate theme options
    valid_modes = ["light", "dark"]
    valid_schemes = ["default", "ocean", "forest", "sunset", "purple"]

    if theme_mode not in valid_modes:
        theme_mode = "light"
    if color_scheme not in valid_schemes:
        color_scheme = "default"

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

    # Setup authentication
    if username and password:
        auth_dependency = create_auth_dependency(username, password)
    else:
        auth_dependency = no_auth

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request, user: str = Depends(auth_dependency)):
        """Main dashboard page."""
        stats = await db.get_stats()

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "stats": stats,
                "theme_mode": theme_mode,
                "color_scheme": color_scheme,
            },
        )

    @app.get("/api/stats")
    async def get_stats(user: str = Depends(auth_dependency)):
        """Get current statistics."""
        return await db.get_stats()

    @app.get("/api/requests")
    async def get_requests(
        limit: int = 20, offset: int = 0, user: str = Depends(auth_dependency)
    ):
        """Get recent requests with pagination."""
        return await db.get_recent_requests(limit, offset)

    @app.get("/api/requests/{request_id}")
    async def get_request_detail(request_id: int, user: str = Depends(auth_dependency)):
        """Get detailed request information."""
        return await db.get_request_by_id(request_id)

    @app.get("/stats-partial")
    async def stats_partial(request: Request, user: str = Depends(auth_dependency)):
        """Partial template for stats (HTMX)."""
        stats = await db.get_stats()
        return templates.TemplateResponse(
            "partials/stats.html", {"request": request, "stats": stats}
        )

    @app.get("/requests-partial")
    async def requests_partial(
        request: Request,
        page: int = 1,
        limit: int = 20,
        user: str = Depends(auth_dependency),
    ):
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
    async def analytics(request: Request, user: str = Depends(auth_dependency)):
        """Analytics dashboard page."""
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "theme_mode": theme_mode,
                "color_scheme": color_scheme,
            },
        )

    @app.get("/api/analytics")
    async def get_analytics(
        resolution: str = "30s", user: str = Depends(auth_dependency)
    ):
        """Get analytics data for charts."""
        return await db.get_analytics_data(resolution)

    return app
