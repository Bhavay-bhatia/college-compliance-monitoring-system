from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.base import Base, engine
from app.api.routes.compliance import router as compliance_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite/Postgres tables on startup for Phase 0
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AICTE SETU — Modular Monolith Architecture (Phase 0: Baseline & Core 6 Statutory Rules Engine)",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from pathlib import Path
from fastapi.responses import FileResponse

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Include routes
app.include_router(compliance_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Dashboard"])
def get_dashboard():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "AICTE SETU Phase 0 API is running."}

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AICTE SETU Core API",
        "phase": "Phase 0 (Baseline Scaffolding & 6 Core Rules Engine)",
        "version": settings.VERSION
    }

