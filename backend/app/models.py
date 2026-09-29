"""SQLAlchemy models for ApplyTrace."""
from datetime import date
from sqlalchemy import Column, Integer, String, Text, Date, Float
from .database import Base


class Application(Base):
    """One job application Manas tracks."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(200), nullable=False, index=True)
    role = Column(String(200), nullable=False)
    location = Column(String(200), default="")
    # wishlist | applied | interviewing | offered | rejected
    status = Column(String(50), default="wishlist", index=True)
    applied_date = Column(Date, default=date.today)
    jd_text = Column(Text, default="")          # pasted job description
    resume_text = Column(Text, default="")      # resume version used for this application
    link = Column(String(500), default="")      # apply link
    notes = Column(Text, default="")
    match_score = Column(Float, default=None)  # last computed JD↔resume score (0-100)


class ResumeKeyword(Base):
    """Keywords extracted from Manas's resume, with weights.
    Powers the 'missing keywords' and tweak suggestions."""
    __tablename__ = "resume_keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), unique=True, index=True, nullable=False)
    weight = Column(Float, default=1.0)  # higher = more central to his profile


class OAuthToken(Base):
    """Stores OAuth refresh tokens for integrations (e.g. Gmail)."""
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(String(50), unique=True, index=True, nullable=False)  # "gmail"
    refresh_token = Column(Text, nullable=False)
    email = Column(String(200), default="")  # account the token belongs to


class User(Base):
    """ApplyTrace login account (Google sign-in)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, index=True, nullable=False)
    name = Column(String(200), default="")
    picture = Column(String(500), default="")
