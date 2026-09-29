"""Email + password auth for ApplyTrace.

  POST /api/auth/register {email, password, name?} -> {token, user}
  POST /api/auth/login    {email, password}        -> {token, user}

Passwords are hashed with PBKDF2-SHA256 (stdlib) and stored in MySQL.
The frontend stores the JWT and sends it as `Authorization: Bearer <token>`.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import create_token
from ..database import get_db
from ..passwords import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_response(user: models.User) -> schemas.AuthResponse:
    return schemas.AuthResponse(
        token=create_token(user),
        user=schemas.UserOut(id=user.id, email=user.email, name=user.name or ""),
    )


@router.post("/register", response_model=schemas.AuthResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(400, "Please enter a valid email address.")
    if len(payload.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(400, "An account with this email already exists — sign in instead.")
    user = models.User(
        email=email,
        name=payload.name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


@router.post("/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash or ""):
        raise HTTPException(401, "Wrong email or password.")
    return _auth_response(user)
