"""FastAPI monitoring middleware."""

import time
import traceback
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .database import MonitorDatabase


class MonitorMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor FastAPI requests and responses."""

    def __init__(
        self, app, db_path: Optional[str] = None, exclude_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.db = MonitorDatabase(db_path or "monitor.db")
        self.exclude_paths = exclude_paths or ["/monitor"]

    async def dispatch(self, request: Request, call_next):
        # Skip monitoring for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        start_time = time.time()

        # Capture request body
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_body = body.decode("utf-8") if body else None
            except Exception:
                request_body = None

        # Capture request data
        request_data = {
            "method": request.method,
            "path": str(request.url.path),
            "query_params": str(request.url.query),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "timestamp": start_time,
            "request_body": request_body,
        }

        # Get request size
        content_length = request.headers.get("content-length")
        request_data["request_size"] = int(content_length) if content_length else 0

        response = None
        error_info = None
        exception_occurred = None
        response_body = None

        try:
            response = await call_next(request)

            # Capture response body
            if response.headers.get("content-type", "").startswith(
                ("application/json", "text/")
            ):
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                try:
                    response_body = body.decode("utf-8")
                except Exception:
                    response_body = None

                # Recreate response with captured body
                from starlette.responses import Response

                response = Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

        except Exception as e:
            exception_occurred = e
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
            }
        finally:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Capture response data
            response_data = {
                "status_code": response.status_code if response else 500,
                "response_time": response_time,
                "response_size": len(response_body.encode("utf-8"))
                if response_body
                else 0,
                "response_headers": dict(response.headers) if response else None,
                "response_body": response_body,
            }

            # Store in database
            await self.db.store_request(
                **request_data, **response_data, error_info=error_info
            )

            # Re-raise exception if one occurred
            if exception_occurred:
                raise exception_occurred

        return response
