"""My Meeting Recording - Main entry point."""

import uvicorn
from internal.api import app


def main():
    """Start the web server."""
    # Run database migrations
    from scripts.migrate import apply_migrations
    apply_migrations("data/meetings.db", "migrations")

    # Initialize preset templates
    from scripts.init_templates import init_preset_templates
    init_preset_templates("data/meetings.db")

    # Run audio cleanup on startup
    from internal.services.audio_cleaner import cleanup_job
    try:
        print("Running audio cleanup on startup...")
        cleanup_job("data/meetings.db")
    except Exception as err:
        print(f"Audio cleanup skipped: {err}")

    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
