"""FastAPI Monitor - Monitoring middleware with dashboard."""

from .dashboard import create_dashboard_app
from .middleware import MonitorMiddleware

__version__ = "0.1.0"
__all__ = ["MonitorMiddleware", "create_dashboard_app"]
