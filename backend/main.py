"""
FastAPI Backend - Main Application Entry Point
================================================
CV/Resume Screener API

Run with:
    uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config import FRONTEND_ORIGIN

# Initialize FastAPI app
app = FastAPI(
    title="CV Resume Screener API",
    description="ML-powered resume screening, classification, and job matching API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow Flask frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN, "http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Pre-load ML models on startup for faster first request."""
    try:
        from backend.ml.classifier import classifier
        classifier.load_models()
    except FileNotFoundError:
        print("[WARNING] ML models not found. Run 'python -m backend.train_model' first.")
    except Exception as e:
        print(f"[WARNING] Could not pre-load models: {e}")


@app.get("/")
async def root():
    return {
        "message": "CV Resume Screener API",
        "docs": "/docs",
        "health": "/api/health"
    }
