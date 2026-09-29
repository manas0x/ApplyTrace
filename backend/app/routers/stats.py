"""Dashboard stats + seed data endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api", tags=["stats"])

STATUSES = ["wishlist", "applied", "interviewing", "offered", "rejected"]


@router.get("/stats", response_model=schemas.StatsResponse)
def stats(db: Session = Depends(get_db)):
    counts = {s: db.query(models.Application).filter(models.Application.status == s).count()
              for s in STATUSES}
    return schemas.StatsResponse(total=sum(counts.values()), **counts)


# Realistic Indian-fresher seed data (2027 batch context).
SEED_APPLICATIONS = [
    {
        "company": "Heizen", "role": "Software Engineer (Fullstack + React Native)",
        "location": "Remote", "status": "applied", "applied_date": date(2026, 9, 26),
        "link": "https://example.com/apply/heizen",
        "notes": "Shortlisted top of the list. Tailor resume around React Native.",
    },
    {
        "company": "HARMAN", "role": "Associate Engineer AI/ML",
        "location": "Bengaluru", "status": "interviewing", "applied_date": date(2026, 9, 24),
        "jd_text": "We are hiring Associate Engineer AI/ML. Skills: Python, FastAPI, MySQL, JWT auth, REST APIs, machine learning fundamentals, data pipelines.",
        "notes": "JD mentions FastAPI, JWT, MySQL — strong match.",
    },
    {
        "company": "Vidyalai", "role": "Full Stack Developer Intern",
        "location": "Kochi", "status": "applied", "applied_date": date(2026, 9, 27),
        "link": "https://example.com/apply/vidyalai",
        "notes": "2027 batch eligible.",
    },
    {
        "company": "MantraCare", "role": "Full Stack Developer Intern",
        "location": "Delhi", "status": "wishlist", "applied_date": date(2026, 9, 29),
        "notes": "Check stipend details before applying.",
    },
]

SEED_RESUME = (
    "Manas Arora — BTech CSE (DIT University, 2027). Frontend developer: React.js, "
    "JavaScript, TypeScript, Tailwind CSS. Backend: FastAPI, MySQL, JWT auth, REST APIs. "
    "Data Engineering Intern at Celebal Technologies: Azure Data Factory, Azure Storage, "
    "Apache Spark, SQL, Delta Lake. Projects: PYQ Solution (React + FastAPI + MySQL), "
    "InvoiceFlow billing app, portfolio site. 300+ LeetCode problems solved."
)


@router.post("/seed", status_code=201)
def seed(db: Session = Depends(get_db)):
    """Idempotent: only seeds when the applications table is empty."""
    if db.query(models.Application).count() > 0:
        return {"seeded": 0, "message": "Applications already exist; skipping."}
    n = 0
    for item in SEED_APPLICATIONS:
        db.add(models.Application(**item))
        n += 1
    # Pre-fill the keyword table from Manas's resume profile.
    from ..matcher import extract_jd_keywords
    if db.query(models.ResumeKeyword).count() == 0:
        for term, w in extract_jd_keywords(SEED_RESUME, top_n=30):
            db.add(models.ResumeKeyword(keyword=term, weight=round(w, 4)))
    db.commit()
    return {"seeded": n, "message": f"Seeded {n} example applications + resume keywords."}
