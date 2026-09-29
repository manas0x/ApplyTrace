"""Dashboard stats + demo-data cleanup."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api", tags=["stats"])

STATUSES = ["wishlist", "applied", "interviewing", "offered", "rejected"]


@router.get("/stats", response_model=schemas.StatsResponse)
def stats(db: Session = Depends(get_db)):
    counts = {s: db.query(models.Application).filter(models.Application.status == s).count()
              for s in STATUSES}
    return schemas.StatsResponse(total=sum(counts.values()), **counts)


# The original 4 seeded demo applications (company, role) — the only rows
# the cleanup endpoint is allowed to delete.
DEMO_APPLICATIONS = [
    ("Heizen", "Software Engineer (Fullstack + React Native)"),
    ("HARMAN", "Associate Engineer AI/ML"),
    ("Vidyalai", "Full Stack Developer Intern"),
    ("MantraCare", "Full Stack Developer Intern"),
]


@router.post("/demo/clear")
def clear_demo(db: Session = Depends(get_db)):
    """Delete only the seeded demo applications. Real entries are untouched."""
    removed = 0
    for company, role in DEMO_APPLICATIONS:
        rows = (
            db.query(models.Application)
            .filter(models.Application.company == company, models.Application.role == role)
            .all()
        )
        for r in rows:
            db.delete(r)
            removed += 1
    db.commit()
    return {"removed": removed}
