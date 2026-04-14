"""API package exports."""

from fastapi import FastAPI
from internal.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="My Meeting Recording",
    description="AI-powered meeting recording and transcription tool",
    version="0.1.0"
)

# Include routes
app.include_router(router)

__all__ = ["app", "router"]
