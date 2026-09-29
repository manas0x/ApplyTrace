"""ApplyTrace API — job application tracker + resume matcher."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import applications, analysis, stats

app = FastAPI(title="ApplyTrace API", version="0.1.0")

# Dev CORS: the Vite frontend runs on :5173.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)  # create tables on startup (dev convenience)

app.include_router(applications.router)
app.include_router(analysis.router)
app.include_router(stats.router)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "applytrace"}
