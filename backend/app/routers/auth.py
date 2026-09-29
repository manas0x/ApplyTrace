"""Google sign-in for ApplyTrace.

Flow:
  1. Frontend opens /api/auth/google/url -> Google consent (openid email profile).
  2. Google redirects to /api/auth/google/callback -> user is found/created,
     a JWT is issued, and the browser is sent to the frontend with the token.
"""
import os

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from .. import models
from ..auth import create_token
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://applytrace-seven.vercel.app")
LOGIN_SCOPES = ["openid", "email", "profile"]


def _redirect_uri() -> str:
    return os.getenv(
        "GOOGLE_LOGIN_REDIRECT_URI",
        "https://applytrace-api.vercel.app/api/auth/google/callback",
    )


def _flow() -> Flow:
    # Same serverless note as the Gmail flow: disable auto PKCE, the verifier
    # would be lost between the auth-url call and the callback.
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [_redirect_uri()],
            }
        },
        scopes=LOGIN_SCOPES,
        redirect_uri=_redirect_uri(),
        autogenerate_code_verifier=False,
    )


@router.get("/google/url")
def google_url():
    if not os.getenv("GOOGLE_CLIENT_ID"):
        raise HTTPException(500, "Google login not configured on server")
    flow = _flow()
    url, _ = flow.authorization_url(access_type="offline", prompt="select_account")
    return {"url": url}


@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        creds = _flow().fetch_token(code=code)
    except Exception as e:
        raise HTTPException(400, f"Google sign-in failed: {e}")
    try:
        info = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {creds['access_token']}"},
            timeout=15,
        ).json()
        email = info.get("email", "")
    except Exception as e:
        raise HTTPException(400, f"Could not read Google profile: {e}")
    if not email:
        raise HTTPException(400, "Google did not return an email address")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(email=email, name=info.get("name", ""), picture=info.get("picture", ""))
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_token(user)
    return RedirectResponse(f"{FRONTEND_URL}/login/callback?token={token}")
