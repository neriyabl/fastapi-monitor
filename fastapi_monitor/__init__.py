"""FastAPI Monitor - Monitoring middleware with dashboard."""

from .middleware import MonitorMiddleware
from .dashboard import create_dashboard_app

__version__ = "0.1.0"
__all__ = ["MonitorMiddleware", "create_dashboard_app"]
