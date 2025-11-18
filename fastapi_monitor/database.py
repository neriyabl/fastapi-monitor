"""Database layer for monitoring data."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiosqlite


class MonitorDatabase:
    """SQLite database for storing monitoring data."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    method TEXT NOT NULL,
                    path TEXT NOT NULL,
                    query_params TEXT,
                    status_code INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    request_size INTEGER DEFAULT 0,
                    response_size INTEGER DEFAULT 0,
                    client_ip TEXT,
                    user_agent TEXT,
                    headers TEXT,
                    request_body TEXT,
                    response_body TEXT,
                    response_headers TEXT,
                    error_info TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create indexes for better query performance
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_timestamp ON requests(timestamp)"
            )
            await db.execute("CREATE INDEX IF NOT EXISTS idx_path ON requests(path)")
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_status ON requests(status_code)"
            )

            await db.commit()

    async def store_request(
        self,
        timestamp: float,
        method: str,
        path: str,
        query_params: str,
        status_code: int,
        response_time: float,
        request_size: int = 0,
        response_size: int = 0,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        request_body: Optional[str] = None,
        response_body: Optional[str] = None,
        response_headers: Optional[Dict[str, Any]] = None,
        error_info: Optional[Dict[str, Any]] = None,
    ):
        """Store request data in database."""
        await self.init_db()  # Ensure tables exist

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO requests (
                    timestamp, method, path, query_params, status_code,
                    response_time, request_size, response_size, client_ip,
                    user_agent, headers, request_body, response_body, response_headers, error_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    method,
                    path,
                    query_params,
                    status_code,
                    response_time,
                    request_size,
                    response_size,
                    client_ip,
                    user_agent,
                    json.dumps(headers) if headers else None,
                    request_body,
                    response_body,
                    json.dumps(response_headers) if response_headers else None,
                    json.dumps(error_info) if error_info else None,
                ),
            )
            await db.commit()

    async def get_recent_requests(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get recent requests with pagination."""
        await self.init_db()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT * FROM requests
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """,
                (limit, offset),
            ) as cursor:
                rows = await cursor.fetchall()
                result = []
                for row in rows:
                    row_dict = dict(row)
                    # Format timestamp
                    dt = datetime.fromtimestamp(row_dict["timestamp"])
                    row_dict["formatted_time"] = dt.strftime("%I:%M:%S %p")
                    result.append(row_dict)
                return result

    async def get_request_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific request by ID."""
        await self.init_db()

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM requests WHERE id = ?", (request_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    row_dict = dict(row)
                    dt = datetime.fromtimestamp(row_dict["timestamp"])
                    row_dict["formatted_time"] = dt.strftime("%I:%M:%S %p")
                    # Parse JSON fields
                    if row_dict["headers"]:
                        row_dict["headers"] = json.loads(row_dict["headers"])
                    if row_dict["response_headers"]:
                        row_dict["response_headers"] = json.loads(
                            row_dict["response_headers"]
                        )
                    if row_dict["error_info"]:
                        row_dict["error_info"] = json.loads(row_dict["error_info"])
                    return row_dict

    async def get_requests_over_time(
        self, resolution: str = "30s"
    ) -> List[Dict[str, Any]]:
        """Get requests over time with different resolutions."""
        await self.init_db()

        resolutions = {
            "30s": {"seconds": 30, "duration": 3600, "format": "%H:%M:%S"},
            "1m": {"seconds": 60, "duration": 3600, "format": "%H:%M"},
            "5m": {"seconds": 300, "duration": 7200, "format": "%H:%M"},
            "15m": {"seconds": 900, "duration": 21600, "format": "%H:%M"},
            "30m": {"seconds": 1800, "duration": 43200, "format": "%H:%M"},
            "1h": {"seconds": 3600, "duration": 86400, "format": "%H:00"},
            "1d": {"seconds": 86400, "duration": 604800, "format": "%Y-%m-%d"},
        }

        config = resolutions.get(resolution, resolutions["30s"])

        async with aiosqlite.connect(self.db_path) as db:
            if resolution == "30s":
                async with db.execute(
                    """
                    SELECT
                        strftime('%H:%M', datetime(timestamp, 'unixepoch')) || ':' ||
                        CASE
                            WHEN CAST(strftime('%S', datetime(timestamp, 'unixepoch')) AS INTEGER) < 30 THEN '00'
                            ELSE '30'
                        END as time_slot,
                        COUNT(*) as count
                    FROM requests
                    WHERE timestamp > (strftime('%s', 'now') - ?)
                    GROUP BY time_slot
                    ORDER BY time_slot
                """,
                    (config["duration"],),
                ) as cursor:
                    return [
                        {"time": row[0], "count": row[1]}
                        for row in await cursor.fetchall()
                    ]
            else:
                async with db.execute(
                    f"""
                    SELECT
                        strftime('{config["format"]}', datetime(
                            (CAST(timestamp AS INTEGER) / {config["seconds"]}) * {config["seconds"]},
                            'unixepoch'
                        )) as time_slot,
                        COUNT(*) as count
                    FROM requests
                    WHERE timestamp > (strftime('%s', 'now') - ?)
                    GROUP BY time_slot
                    ORDER BY time_slot
                """,
                    (config["duration"],),
                ) as cursor:
                    return [
                        {"time": row[0], "count": row[1]}
                        for row in await cursor.fetchall()
                    ]

    async def get_analytics_data(self, resolution: str = "30s") -> Dict[str, Any]:
        """Get analytics data for charts."""
        await self.init_db()

        requests_over_time = await self.get_requests_over_time(resolution)

        async with aiosqlite.connect(self.db_path) as db:
            # Response time distribution
            async with db.execute(
                """
                SELECT
                    CASE
                        WHEN response_time < 100 THEN '0-100ms'
                        WHEN response_time < 500 THEN '100-500ms'
                        WHEN response_time < 1000 THEN '500ms-1s'
                        WHEN response_time < 5000 THEN '1-5s'
                        ELSE '5s+'
                    END as range,
                    COUNT(*) as count
                FROM requests
                GROUP BY range
            """
            ) as cursor:
                response_time_dist = [
                    {"range": row[0], "count": row[1]}
                    for row in await cursor.fetchall()
                ]

            # Top endpoints
            async with db.execute(
                """
                SELECT path, COUNT(*) as count, AVG(response_time) as avg_time
                FROM requests
                GROUP BY path
                ORDER BY count DESC
                LIMIT 10
            """
            ) as cursor:
                top_endpoints = [
                    {"path": row[0], "count": row[1], "avg_time": round(row[2], 2)}
                    for row in await cursor.fetchall()
                ]

            # Status code trends (last 7 days)
            async with db.execute(
                """
                SELECT
                    date(datetime(timestamp, 'unixepoch')) as date,
                    status_code,
                    COUNT(*) as count
                FROM requests
                WHERE timestamp > (strftime('%s', 'now') - 604800)
                GROUP BY date, status_code
                ORDER BY date, status_code
            """
            ) as cursor:
                status_trends = [
                    {"date": row[0], "status_code": row[1], "count": row[2]}
                    for row in await cursor.fetchall()
                ]

            return {
                "requests_over_time": requests_over_time,
                "resolution": resolution,
                "response_time_distribution": response_time_dist,
                "top_endpoints": top_endpoints,
                "status_trends": status_trends,
            }

    async def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        await self.init_db()

        async with aiosqlite.connect(self.db_path) as db:
            # Total requests
            async with db.execute("SELECT COUNT(*) as total FROM requests") as cursor:
                total_requests = (await cursor.fetchone())[0]

            # Average response time
            async with db.execute(
                "SELECT AVG(response_time) as avg_time FROM requests"
            ) as cursor:
                avg_response_time = (await cursor.fetchone())[0] or 0

            # Status code distribution
            async with db.execute(
                """
                SELECT status_code, COUNT(*) as count
                FROM requests
                GROUP BY status_code
            """
            ) as cursor:
                status_codes = {str(row[0]): row[1] for row in await cursor.fetchall()}

            # Error count
            async with db.execute(
                "SELECT COUNT(*) as errors FROM requests WHERE error_info IS NOT NULL"
            ) as cursor:
                error_count = (await cursor.fetchone())[0]

            return {
                "total_requests": total_requests,
                "avg_response_time": round(avg_response_time, 2),
                "status_codes": status_codes,
                "error_count": error_count,
            }
