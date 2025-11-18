"""Example FastAPI app with authenticated monitoring dashboard."""

from fastapi import FastAPI

from fastapi_monitor import MonitorMiddleware, create_dashboard_app

# Create FastAPI app
app = FastAPI(title="My Secure API")

# Add monitoring middleware
app.add_middleware(MonitorMiddleware, db_path="monitor.db")


# Your API routes
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}


@app.get("/public")
async def public_endpoint():
    return {"message": "This is public"}


# Create dashboard with basic authentication
dashboard_app = create_dashboard_app(
    db_path="monitor.db",
    username="admin",  # Set your username
    password="secret123",  # Set your password
)

# Mount the protected dashboard
app.mount("/monitor", dashboard_app)

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting server...")
    print("📊 Dashboard: http://localhost:8000/monitor")
    print("🔐 Username: admin")
    print("🔑 Password: secret123")
    uvicorn.run(app, host="0.0.0.0", port=8000)
