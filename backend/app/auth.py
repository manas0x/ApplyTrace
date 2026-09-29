"""JWT session handling for ApplyTrace login.

Login is via Google OAuth (see routers/auth.py). On success the backend
issues a signed JWT; the frontend stores it and sends it as
`Authorization: Bearer <token>` on every API call.
"""
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from . import models

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGO = "HS256"
JWT_DAYS = 30

_bearer = HTTPBearer(auto_error=False)


def create_token(user: models.User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(days=JWT_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> models.User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Not signed in")
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired session — please sign in again")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(401, "Account not found — please sign in again")
    return user
