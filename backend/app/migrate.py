"""Lightweight migrations for columns that create_all() can't add to
tables that already exist (e.g. the users table created before password_hash)."""
from sqlalchemy import inspect, text


def ensure_columns(engine) -> None:
    try:
        insp = inspect(engine)
        if "users" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("users")}
        if "password_hash" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) DEFAULT ''"))
    except Exception:
        # Never crash startup on a best-effort migration.
        pass
