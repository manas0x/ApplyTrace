"""Gmail connect + "Sync from Gmail" endpoints."""
import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .. import gmail_sync, models
from ..database import get_db

router = APIRouter(prefix="/api/gmail", tags=["gmail"])

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://applytrace-seven.vercel.app")


def _token(db: Session) -> models.OAuthToken | None:
    return db.query(models.OAuthToken).filter(models.OAuthToken.service == "gmail").first()


@router.get("/status")
def status(db: Session = Depends(get_db)):
    tok = _token(db)
    return {"connected": tok is not None, "email": tok.email if tok else None}


@router.get("/auth-url")
def auth_url():
    if not os.getenv("GOOGLE_CLIENT_ID"):
        raise HTTPException(500, "Gmail not configured on server (missing GOOGLE_CLIENT_ID)")
    return {"url": gmail_sync.auth_url()}


@router.get("/callback")
def callback(code: str, db: Session = Depends(get_db)):
    """Google redirects here after consent. Stores the refresh token, then
    sends the user back to the frontend."""
    try:
        creds = gmail_sync.exchange_code(code)
    except Exception as e:
        raise HTTPException(400, f"OAuth exchange failed: {e}")

    email = ""
    if creds.refresh_token:
        try:
            service = gmail_sync.get_service(creds.refresh_token)
            email = service.users().getProfile(userId="me").execute().get("emailAddress", "")
        except Exception:
            pass

    tok = _token(db)
    if not tok:
        tok = models.OAuthToken(service="gmail", refresh_token="")
        db.add(tok)
    if creds.refresh_token:
        tok.refresh_token = creds.refresh_token
    tok.email = email or tok.email
    db.commit()
    return RedirectResponse(f"{FRONTEND_URL}/?gmail=connected")


@router.post("/sync")
def sync(db: Session = Depends(get_db)):
    """Scan Gmail for application signals and add missing applications."""
    tok = _token(db)
    if not tok or not tok.refresh_token:
        raise HTTPException(400, "Gmail not connected — connect it first, then sync.")
    try:
        service = gmail_sync.get_service(tok.refresh_token)
        found = gmail_sync.scan(service)
    except Exception as e:
        raise HTTPException(502, f"Gmail scan failed: {e}")

    existing = {
        ((a.company or "").strip().lower(), (a.role or "").strip().lower())
        for a in db.query(models.Application).all()
    }
    added, skipped = 0, 0
    companies: set[str] = set()
    for f in found:
        key = (f["company"].strip().lower(), f["role"].strip().lower())
        if key in existing:
            skipped += 1
            continue
        db.add(
            models.Application(
                company=f["company"],
                role=f["role"],
                location="",
                status="applied",
                applied_date=f["applied_date"] or date.today(),
                notes=f"Auto-detected from Gmail ({f['correspondent']} — {f['subject']})",
            )
        )
        existing.add(key)
        added += 1
        companies.add(f["company"])
    db.commit()
    return {"added": added, "skipped": skipped, "companies": sorted(companies)}
