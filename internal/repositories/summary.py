"""Summary repository."""

import sqlite3
from typing import List, Optional
from datetime import datetime
from internal.repositories.base import BaseRepository
from internal.domain.summary import Summary


class SummaryRepository(BaseRepository):
    """Repository for Summary entity."""

    def create(self, summary: Summary) -> None:
        """
        Create a new summary.

        Args:
            summary: Summary entity to create
        """
        if summary.created_at is None:
            summary.created_at = datetime.now()

        self.execute(
            """
            INSERT INTO summaries (id, meeting_id, version, prompt, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (summary.id, summary.meeting_id, summary.version,
             summary.prompt, summary.content, summary.created_at)
        )
        self.commit()

    def get_by_id(self, summary_id: str) -> Optional[Summary]:
        """
        Retrieve summary by ID.

        Args:
            summary_id: Summary ID

        Returns:
            Summary entity or None if not found
        """
        row = self.fetch_one(
            "SELECT * FROM summaries WHERE id = ?",
            (summary_id,)
        )

        if not row:
            return None

        return self._row_to_summary(row)

    def get_by_meeting(self, meeting_id: str) -> List[Summary]:
        """
        Retrieve all summaries for a meeting.

        Args:
            meeting_id: Meeting ID

        Returns:
            List of Summary entities ordered by version
        """
        rows = self.fetch_all(
            "SELECT * FROM summaries WHERE meeting_id = ? ORDER BY version ASC",
            (meeting_id,)
        )
        return [self._row_to_summary(row) for row in rows]

    def get_latest_by_meeting(self, meeting_id: str) -> Optional[Summary]:
        """
        Retrieve the latest summary for a meeting.

        Args:
            meeting_id: Meeting ID

        Returns:
            Latest Summary entity or None if not found
        """
        row = self.fetch_one(
            "SELECT * FROM summaries WHERE meeting_id = ? ORDER BY version DESC LIMIT 1",
            (meeting_id,)
        )

        if not row:
            return None

        return self._row_to_summary(row)

    def delete(self, summary_id: str) -> None:
        """
        Delete a summary by ID.

        Args:
            summary_id: Summary ID to delete
        """
        self.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
        self.commit()

    def _row_to_summary(self, row: tuple) -> Summary:
        """Convert database row to Summary entity."""
        (id_, meeting_id, version, prompt, content, created_at) = row

        return Summary(
            id=id_,
            meeting_id=meeting_id,
            version=version,
            prompt=prompt,
            content=content,
            created_at=datetime.fromisoformat(created_at) if created_at else None
        )
