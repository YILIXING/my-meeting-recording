"""Audio cleanup scheduler service."""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class AudioCleanupService:
    """Service for cleaning up old audio files."""

    AUDIO_RETENTION_DAYS = 7

    def __init__(self, db_path: str = "data/meetings.db"):
        """
        Initialize audio cleanup service.

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path

    def cleanup_expired_audios(self) -> dict:
        """
        Clean up audio files older than retention period.

        Returns:
            Dict with cleanup statistics
        """
        cutoff_date = datetime.now() - timedelta(days=self.AUDIO_RETENTION_DAYS)

        # Get meetings with expired audio
        meetings = self._get_meetings_with_audio_older_than(cutoff_date)

        cleaned_count = 0
        errors = []

        for meeting in meetings:
            try:
                self._delete_audio_for_meeting(meeting)
                cleaned_count += 1
            except Exception as err:
                errors.append({
                    "meeting_id": meeting["id"],
                    "error": str(err)
                })

        return {
            "cleaned_count": cleaned_count,
            "error_count": len(errors),
            "errors": errors
        }

    def _get_meetings_with_audio_older_than(self, cutoff_date: datetime) -> List[dict]:
        """Get meetings with audio older than cutoff date."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, audio_path, created_at
            FROM meetings
            WHERE audio_path IS NOT NULL
              AND audio_deleted_at IS NULL
              AND created_at < ?
            ORDER BY created_at ASC
        """, (cutoff_date.isoformat(),))

        meetings = []
        for row in cursor.fetchall():
            meetings.append({
                "id": row[0],
                "audio_path": row[1],
                "created_at": row[2]
            })

        conn.close()
        return meetings

    def _delete_audio_for_meeting(self, meeting: dict) -> None:
        """Delete audio file and mark as deleted in database."""
        meeting_id = meeting["id"]
        audio_path = meeting["audio_path"]

        # Delete physical file
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

        # Mark as deleted in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE meetings
            SET audio_deleted_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), meeting_id))

        conn.commit()
        conn.close()

    def get_audio_storage_info(self) -> dict:
        """Get information about audio storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get total size
        cursor.execute("""
            SELECT
                COUNT(*) as total_count,
                SUM(CASE WHEN audio_deleted_at IS NULL THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN audio_deleted_at IS NOT NULL THEN 1 ELSE 0 END) as deleted_count
            FROM meetings
            WHERE audio_path IS NOT NULL
        """)

        row = cursor.fetchone()
        stats = {
            "total_count": row[0] if row[0] else 0,
            "active_count": row[1] if row[1] else 0,
            "deleted_count": row[2] if row[2] else 0
        }

        # Calculate storage size (if possible)
        total_size = 0
        cursor.execute("SELECT audio_path FROM meetings WHERE audio_path IS NOT NULL AND audio_deleted_at IS NULL")
        for row in cursor.fetchall():
            audio_path = row[0]
            if audio_path and os.path.exists(audio_path):
                total_size += os.path.getsize(audio_path)

        stats["total_size_bytes"] = total_size
        stats["total_size_mb"] = round(total_size / 1024 / 1024, 2)

        conn.close()
        return stats


def cleanup_job(db_path: str = "data/meetings.db") -> None:
    """
    Run the audio cleanup job.

    Args:
        db_path: Path to database file
    """
    service = AudioCleanupService(db_path)
    result = service.cleanup_expired_audios()

    print(f"Audio cleanup completed:")
    print(f"  Cleaned: {result['cleaned_count']} files")
    if result['error_count'] > 0:
        print(f"  Errors: {result['error_count']}")
        for error in result['errors']:
            print(f"    - Meeting {error['meeting_id']}: {error['error']}")


if __name__ == "__main__":
    cleanup_job()
