"""ApplyTrace API — job application tracker + resume matcher."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import applications, analysis, stats, gmail

app = FastAPI(title="ApplyTrace API", version="0.1.0")

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

app.include_router(applications.router)
app.include_router(analysis.router)
app.include_router(stats.router)
app.include_router(gmail.router)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "applytrace"}
