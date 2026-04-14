"""Meeting repository."""

import sqlite3
from typing import List, Optional
from datetime import datetime
from internal.repositories.base import BaseRepository
from internal.domain.meeting import Meeting, MeetingStatus


class MeetingRepository(BaseRepository):
    """Repository for Meeting entity."""

    def create(self, meeting: Meeting) -> None:
        """
        Create a new meeting.

        Args:
            meeting: Meeting entity to create
        """
        now = datetime.now()
        if meeting.created_at is None:
            meeting.created_at = now
        if meeting.updated_at is None:
            meeting.updated_at = now

        self.execute(
            """
            INSERT INTO meetings (
                id, title, original_filename, audio_path, status,
                progress, error_message, created_at, updated_at, audio_deleted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meeting.id,
                meeting.title,
                meeting.original_filename,
                meeting.audio_path,
                meeting.status.value,
                meeting.progress,
                meeting.error_message,
                meeting.created_at,
                meeting.updated_at,
                meeting.audio_deleted_at
            )
        )
        self.commit()

    def get_by_id(self, meeting_id: str) -> Optional[Meeting]:
        """
        Retrieve meeting by ID.

        Args:
            meeting_id: Meeting ID

        Returns:
            Meeting entity or None if not found
        """
        row = self.fetch_one(
            "SELECT * FROM meetings WHERE id = ?",
            (meeting_id,)
        )

        if not row:
            return None

        return self._row_to_meeting(row)

    def update(self, meeting: Meeting) -> None:
        """
        Update an existing meeting.

        Args:
            meeting: Meeting entity with updated fields
        """
        meeting.updated_at = datetime.now()

        self.execute(
            """
            UPDATE meetings SET
                title = ?, audio_path = ?, status = ?, progress = ?,
                error_message = ?, updated_at = ?, audio_deleted_at = ?
            WHERE id = ?
            """,
            (
                meeting.title,
                meeting.audio_path,
                meeting.status.value,
                meeting.progress,
                meeting.error_message,
                meeting.updated_at,
                meeting.audio_deleted_at,
                meeting.id
            )
        )
        self.commit()

    def delete(self, meeting_id: str) -> None:
        """
        Delete a meeting by ID.

        Args:
            meeting_id: Meeting ID to delete
        """
        self.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
        self.commit()

    def list_all(self) -> List[Meeting]:
        """
        List all meetings ordered by creation time.

        Returns:
            List of Meeting entities
        """
        rows = self.fetch_all(
            "SELECT * FROM meetings ORDER BY created_at DESC"
        )
        return [self._row_to_meeting(row) for row in rows]

    def list_by_status(self, status: MeetingStatus) -> List[Meeting]:
        """
        List meetings by status.

        Args:
            status: Meeting status to filter by

        Returns:
            List of Meeting entities with the specified status
        """
        rows = self.fetch_all(
            "SELECT * FROM meetings WHERE status = ? ORDER BY created_at DESC",
            (status.value,)
        )
        return [self._row_to_meeting(row) for row in rows]

    def _row_to_meeting(self, row: tuple) -> Meeting:
        """
        Convert database row to Meeting entity.

        Args:
            row: Database row tuple

        Returns:
            Meeting entity
        """
        (
            id_, title, original_filename, audio_path, status_str,
            progress, error_message, created_at, updated_at, audio_deleted_at
        ) = row

        return Meeting(
            id=id_,
            title=title,
            original_filename=original_filename,
            audio_path=audio_path,
            status=MeetingStatus(status_str),
            progress=progress,
            error_message=error_message,
            created_at=datetime.fromisoformat(created_at) if created_at else None,
            updated_at=datetime.fromisoformat(updated_at) if updated_at else None,
            audio_deleted_at=datetime.fromisoformat(audio_deleted_at) if audio_deleted_at else None
        )
