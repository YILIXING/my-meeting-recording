"""API package exports."""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from internal.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="My Meeting Recording",
    description="AI-powered meeting recording and transcription tool",
    version="1.0.0"
)


# Root redirect to home page
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root path to the home page."""
    return RedirectResponse(url="/static/index.html")


# Include API routes
app.include_router(router)

__all__ = ["app", "router"]
