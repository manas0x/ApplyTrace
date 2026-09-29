"""CRUD endpoints for applications."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[schemas.ApplicationOut])
def list_applications(status: str | None = Query(default=None), db: Session = Depends(get_db)):
    q = db.query(models.Application)
    if status:
        q = q.filter(models.Application.status == status)
    return q.order_by(models.Application.id.desc()).all()


@router.post("", response_model=schemas.ApplicationOut, status_code=201)
def create_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    app = models.Application(**payload.model_dump())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("/{app_id}", response_model=schemas.ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.get(models.Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    return app


@router.patch("/{app_id}", response_model=schemas.ApplicationOut)
def update_application(app_id: int, payload: schemas.ApplicationUpdate, db: Session = Depends(get_db)):
    app = db.get(models.Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.get(models.Application, app_id)
    if not app:
        raise HTTPException(404, "Application not found")
    db.delete(app)
    db.commit()
