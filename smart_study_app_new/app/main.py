from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from pathlib import Path

from . import models
from .database import engine, get_db
from .config import settings
from .api.endpoints import users, auth, materials, ai_processing, study_sessions, analytics

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Study App API",
    description="API for the Smart Study App - An AI-powered learning platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded materials
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_FOLDER), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(users.router, prefix="/api")
app.include_router(materials.router, prefix="/api")
app.include_router(ai_processing.router, prefix="/api")
app.include_router(study_sessions.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Smart Study App API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Study App API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Run with uvicorn programmatically
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
