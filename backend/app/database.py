"""Database engine/session wiring.

MySQL-ready: set DATABASE_URL to a mysql+pymysql URL (see .env.example).
Defaults to a local SQLite file for zero-setup local runs.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./applytrace.db")

# Vercel serverless: only /tmp is writable, and the filesystem is ephemeral
# (data resets between deployments/cold starts — fine for a demo, use a
# hosted DB via DATABASE_URL for persistence).
if os.getenv("VERCEL") and DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = "sqlite:////tmp/applytrace.db"

# SQLite needs this for threaded servers; other drivers don't.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

if DATABASE_URL.startswith("mysql"):
    # Hosted MySQL (e.g. Aiven) enforces encrypted connections. Use TLS
    # without pinning a CA cert (server still encrypts; fine for this app).
    import ssl as _ssl

    _ctx = _ssl.create_default_context()
    _ctx.check_hostname = False
    _ctx.verify_mode = _ssl.CERT_NONE
    connect_args = {"ssl": _ctx}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
