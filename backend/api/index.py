"""Vercel serverless entrypoint.

Vercel's Python runtime treats files under `api/` as serverless functions and
natively serves an ASGI `app`. This thin wrapper re-exports the FastAPI app so
the same codebase runs locally (uvicorn) and on Vercel unchanged.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app  # noqa: E402,F401  (Vercel looks for `app`)
