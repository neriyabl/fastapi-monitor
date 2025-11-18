"""Example FastAPI app with advanced theme system."""

from fastapi import FastAPI

from fastapi_monitor import MonitorMiddleware, create_dashboard_app

# Create FastAPI app
app = FastAPI(title="My Themed API")

# Add monitoring middleware
app.add_middleware(MonitorMiddleware, db_path="monitor.db")


# Your API routes
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}


# Example 1: Light mode with Ocean color scheme
dashboard_light_ocean = create_dashboard_app(
    db_path="monitor.db",
    theme_mode="light",  # light or dark
    color_scheme="ocean",  # default, ocean, forest, sunset, purple
)

# Example 2: Dark mode with Forest color scheme
dashboard_dark_forest = create_dashboard_app(
    db_path="monitor.db", theme_mode="dark", color_scheme="forest"
)

# Example 3: With authentication and custom theme
dashboard_auth_sunset = create_dashboard_app(
    db_path="monitor.db",
    username="admin",
    password="secret123",
    theme_mode="light",
    color_scheme="sunset",
)

# Mount different themed dashboards
app.mount("/monitor", dashboard_light_ocean)  # Light Ocean theme
app.mount("/monitor-dark", dashboard_dark_forest)  # Dark Forest theme
app.mount("/monitor-auth", dashboard_auth_sunset)  # Light Sunset with auth

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting server with multiple themed dashboards...")
    print("🌊 Light Ocean: http://localhost:8000/monitor")
    print("🌲 Dark Forest: http://localhost:8000/monitor-dark")
    print("🌅 Light Sunset (auth): http://localhost:8000/monitor-auth")
    print("   └── Username: admin, Password: secret123")
    print("\n💡 Users can also switch themes dynamically in the UI!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
