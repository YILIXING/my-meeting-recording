"""API package exports."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from internal.api.routes import router

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "static"

# Create FastAPI app
app = FastAPI(
    title="My Meeting Recording",
    description="AI-powered meeting recording and transcription tool",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Root redirect to home page
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to the home page."""
    return RedirectResponse(url="/static/index.html")

# Include API routes
app.include_router(router)

__all__ = ["app", "router"]
