"""Basic authentication for dashboard."""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def create_auth_dependency(username: str, password: str):
    """Create authentication dependency with given credentials."""

    def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
        correct_username = secrets.compare_digest(credentials.username, username)
        correct_password = secrets.compare_digest(credentials.password, password)

        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    return authenticate


def no_auth():
    """No authentication required."""
    return None
