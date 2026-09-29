"""Resume↔JD analysis endpoints (stdlib TF matcher, no external API)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, matcher

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.post("", response_model=schemas.AnalyzeResponse)
def analyze_text(payload: schemas.AnalyzeRequest):
    if not payload.jd_text.strip():
        raise HTTPException(400, "jd_text is empty")
    return schemas.AnalyzeResponse(**matcher.analyze(payload.jd_text, payload.resume_text))


@router.post("/application/{app_id}", response_model=schemas.AnalyzeResponse)
def analyze_application(app_id: int, db: Session = Depends(get_db)):
    app = db.get(models.Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    result = matcher.analyze(app.jd_text or "", app.resume_text or "")
    app.match_score = result["score"]
    db.commit()
    return schemas.AnalyzeResponse(**result)
