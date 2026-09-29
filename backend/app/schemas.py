"""Pydantic request/response schemas."""
from datetime import date
from typing import Optional
from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    company: str
    role: str
    location: str = ""
    status: str = "wishlist"
    applied_date: date = date.today()
    jd_text: str = ""
    resume_text: str = ""
    link: str = ""
    notes: str = ""


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[date] = None
    jd_text: Optional[str] = None
    resume_text: Optional[str] = None
    link: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    company: str
    role: str
    location: str
    status: str
    applied_date: date
    jd_text: str
    resume_text: str
    link: str
    notes: str
    match_score: Optional[float]

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    jd_text: str
    resume_text: str


class AnalyzeResponse(BaseModel):
    score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    suggested_tweaks: list[str]


class StatsResponse(BaseModel):
    total: int
    wishlist: int
    applied: int
    interviewing: int
    offered: int
    rejected: int


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str = ""


class AuthResponse(BaseModel):
    token: str
    user: UserOut
