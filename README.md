# FastAPI Monitor

A lightweight monitoring middleware for FastAPI applications with a built-in dashboard.

## Features

- 🚀 Easy integration with any FastAPI app
- 📊 Real-time dashboard with HTMX
- 💾 Local SQLite storage
- 📈 Comprehensive metrics:
  - Request/response times
  - HTTP status codes
  - Request/response sizes
  - Client IPs and User Agents
  - Error tracking with stack traces
  - Custom metrics support

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_monitor import MonitorMiddleware, create_dashboard_app

# Create your FastAPI app
app = FastAPI()

# Add monitoring middleware
app.add_middleware(MonitorMiddleware, db_path="monitor.db")

# Your routes
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Create and mount dashboard
dashboard_app = create_dashboard_app("monitor.db")
app.mount("/monitor", dashboard_app)
```

## Usage

1. **Add the middleware** to your FastAPI app
2. **Mount the dashboard** at any path (e.g., `/monitor`)
3. **Visit the dashboard** to see real-time monitoring data

## Dashboard Features

- **Auto-refresh** every 5 seconds (toggleable)
- **Real-time stats** - total requests, avg response time, errors
- **Status code distribution** 
- **Recent requests table** with full details
- **Responsive design** for mobile/desktop

## Configuration

```python
# Custom database path
app.add_middleware(MonitorMiddleware, db_path="/path/to/monitor.db")

# Dashboard with custom database
dashboard_app = create_dashboard_app("/path/to/monitor.db")
```

## Example

Run the example:

```bash
cd examples
python example_app.py
```

Then visit:
- Main API: http://localhost:8000
- Dashboard: http://localhost:8000/monitor

## Development

```bash
pip install -e ".[dev]"
pytest
```
