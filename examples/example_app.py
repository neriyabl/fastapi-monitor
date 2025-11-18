"""Example FastAPI app with monitoring."""

import asyncio
import random

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi_monitor import MonitorMiddleware, create_dashboard_app


# Pydantic models
class User(BaseModel):
    name: str
    email: str
    age: int


class UserUpdate(BaseModel):
    name: str = None
    email: str = None
    age: int = None


# Create main app
app = FastAPI(title="Example API")

# Add monitoring middleware
app.add_middleware(
    MonitorMiddleware, db_path="example_monitor.db", exclude_paths=["/monitor"]
)


# Example routes
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/slow")
async def slow_endpoint():
    # Simulate slow response
    await asyncio.sleep(random.uniform(0.5, 2.0))
    return {"message": "This was slow"}


@app.get("/fatal")
async def fatal_error():
    # This will cause a fatal error (unhandled exception)
    raise ZeroDivisionError("Intentional error for testing")
    return {"message": "This won't be reached"}


@app.get("/error")
async def error_endpoint():
    if random.choice([True, False]):
        raise HTTPException(status_code=500, detail="Random error")
    return {"message": "Success"}


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id > 100:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "name": f"User {user_id}"}


@app.post("/users")
async def create_user(user: User):
    # Simulate processing time
    await asyncio.sleep(0.1)
    return {"id": random.randint(1, 1000), **user.dict(), "created": True}


@app.put("/users/{user_id}")
async def update_user(user_id: int, user: User):
    if user_id > 100:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, **user.dict(), "updated": True}


@app.patch("/users/{user_id}")
async def partial_update_user(user_id: int, user: UserUpdate):
    if user_id > 100:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, **user.dict(exclude_unset=True), "patched": True}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    if user_id > 100:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "deleted": True}


# Create dashboard app
dashboard_app = create_dashboard_app("example_monitor.db")

# Mount dashboard
app.mount("/monitor", dashboard_app)

if __name__ == "__main__":
    print("Starting example app...")
    print("Main API: http://localhost:8000")
    print("Dashboard: http://localhost:8000/monitor")
    print("\nExample requests:")
    print("POST /users - Create user")
    print("PUT /users/1 - Update user")
    print("PATCH /users/1 - Partial update user")
    print("DELETE /users/1 - Delete user")
    uvicorn.run(app, host="0.0.0.0", port=8000)
