"""ApplyTrace API — job application tracker + resume matcher."""
import os
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .auth import get_current_user
from .database import Base, engine
from .routers import applications, analysis, stats, gmail, auth, jobs

app = FastAPI(title="ApplyTrace API", version="0.2.0")

# CORS origins from env (comma-separated). Local dev default: Vite on :5173.
# On Vercel, set CORS_ORIGINS to the frontend URL, e.g.
#   CORS_ORIGINS=https://applytrace-seven.vercel.app
cors_origins = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)  # create tables on startup (dev convenience)

# Everything except /api/health and the OAuth callbacks requires login.
authed = [Depends(get_current_user)]
app.include_router(applications.router, dependencies=authed)
app.include_router(analysis.router, dependencies=authed)
app.include_router(stats.router, dependencies=authed)
app.include_router(jobs.router, dependencies=authed)
app.include_router(auth.router)  # public: login flow
# Gmail: public only for Google's OAuth callback; the rest needs login
# (per-endpoint dependencies are set inside the gmail router).
app.include_router(gmail.router)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "applytrace"}
