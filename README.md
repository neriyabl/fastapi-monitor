# FastAPI Monitor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A lightweight, production-ready monitoring middleware for FastAPI applications with real-time dashboard and comprehensive metrics collection.

## ✨ Features

- 🚀 **Zero-configuration setup** - Add monitoring in 3 lines of code
- 📊 **Real-time dashboard** with auto-refresh capabilities
- 💾 **SQLite storage** - No external dependencies required
- 📈 **Comprehensive metrics** - Request/response times, status codes, error tracking
- 🔒 **Security-first** - SQL injection proof with parameterized queries
- 📱 **Responsive UI** - Works seamlessly on desktop and mobile
- ⚡ **High performance** - Minimal overhead on your API

## 🚀 Quick Start

### Installation

```bash
pip install fastapi-monitor
```

### Basic Usage

```python
from fastapi import FastAPI
from fastapi_monitor import MonitorMiddleware, create_dashboard_app

app = FastAPI()

# Add monitoring middleware
app.add_middleware(MonitorMiddleware, db_path="monitor.db")

# Your API routes
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Mount the monitoring dashboard
dashboard_app = create_dashboard_app("monitor.db")
app.mount("/monitor", dashboard_app)
```

That's it! Visit `http://localhost:8000/monitor` to see your API metrics.

## 📊 Dashboard Features

- **Real-time statistics** - Total requests, average response time, error rates
- **Request timeline** - Visual representation of API traffic over time
- **Status code distribution** - HTTP status code breakdown with color coding
- **Error tracking** - Detailed error logs with stack traces
- **Request details** - Full request/response inspection
- **Performance metrics** - Response time analysis and trends

## ⚙️ Configuration

### Advanced Middleware Setup

```python
app.add_middleware(
    MonitorMiddleware,
    db_path="custom_monitor.db",
    exclude_paths=["/health", "/metrics", "/docs"]
)
```

### Custom Dashboard Mount

```python
dashboard_app = create_dashboard_app("custom_monitor.db")
app.mount("/admin/monitoring", dashboard_app)
```

## 📈 Metrics Collected

| Metric | Description |
|--------|-------------|
| Request Time | Timestamp of each request |
| Response Time | Processing time in milliseconds |
| HTTP Method | GET, POST, PUT, DELETE, etc. |
| Request Path | API endpoint accessed |
| Status Code | HTTP response status |
| Request Size | Size of request body in bytes |
| Response Size | Size of response body in bytes |
| Client IP | Source IP address |
| User Agent | Client browser/application info |
| Error Details | Stack traces for failed requests |

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/fastapi-monitor.git
cd fastapi-monitor
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## 📝 Example Application

Check out the complete example in the `examples/` directory:

```bash
cd examples
python example_app.py
```

Then visit:
- API: http://localhost:8000
- Dashboard: http://localhost:8000/monitor

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [HTMX](https://htmx.org/)
- Database operations with [aiosqlite](https://github.com/omnilib/aiosqlite)

---

**⭐ If this project helped you, please consider giving it a star!**
