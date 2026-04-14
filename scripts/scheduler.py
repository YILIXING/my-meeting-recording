"""Scheduler for periodic tasks."""

import asyncio
import schedule
import time
from internal.services.audio_cleaner import cleanup_job


class TaskScheduler:
    """Scheduler for running periodic tasks."""

    def __init__(self, db_path: str = "data/meetings.db"):
        """
        Initialize task scheduler.

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.running = False

    def setup_jobs(self):
        """Setup scheduled jobs."""
        # Run audio cleanup daily at 2 AM
        schedule.every().day.at("02:00").do(self._run_cleanup)

        # Also run on startup
        schedule.every().day.do(self._run_cleanup)

    def _run_cleanup(self):
        """Run audio cleanup job."""
        try:
            cleanup_job(self.db_path)
        except Exception as err:
            print(f"Error running cleanup job: {err}")

    def start(self):
        """Start the scheduler."""
        if self.running:
            return

        self.running = True
        self.setup_jobs()

        print("Task scheduler started")

        # Run immediately on startup
        self._run_cleanup()

        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        print("Task scheduler stopped")


def run_scheduler(db_path: str = "data/meetings.db"):
    """
    Run the task scheduler in blocking mode.

    Args:
        db_path: Path to database file
    """
    scheduler = TaskScheduler(db_path)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()


if __name__ == "__main__":
    run_scheduler()
