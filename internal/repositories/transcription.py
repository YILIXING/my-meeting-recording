"""Transcription repository."""

import sqlite3
from typing import List, Optional
from datetime import datetime
from internal.repositories.base import BaseRepository
from internal.domain.transcription import TranscriptSegment, SpeakerMapping


class TranscriptionRepository(BaseRepository):
    """Repository for TranscriptSegment and SpeakerMapping entities."""

    def create_segment(self, segment: TranscriptSegment) -> None:
        """
        Create a new transcript segment.

        Args:
            segment: TranscriptSegment entity to create
        """
        if segment.created_at is None:
            segment.created_at = datetime.now()

        self.execute(
            """
            INSERT INTO transcript_segments (id, meeting_id, speaker_id, start_time, end_time, text, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (segment.id, segment.meeting_id, segment.speaker_id,
             segment.start_time, segment.end_time, segment.text, segment.created_at)
        )
        self.commit()

    def get_segments_by_meeting(self, meeting_id: str) -> List[TranscriptSegment]:
        """
        Retrieve all transcript segments for a meeting.

        Args:
            meeting_id: Meeting ID

        Returns:
            List of TranscriptSegment entities ordered by start_time
        """
        rows = self.fetch_all(
            "SELECT * FROM transcript_segments WHERE meeting_id = ? ORDER BY start_time",
            (meeting_id,)
        )
        return [self._row_to_segment(row) for row in rows]

    def delete_segments_by_meeting(self, meeting_id: str) -> None:
        """
        Delete all transcript segments for a meeting.

        Args:
            meeting_id: Meeting ID
        """
        self.execute(
            "DELETE FROM transcript_segments WHERE meeting_id = ?",
            (meeting_id,)
        )
        self.commit()

    def create_speaker_mapping(
        self,
        meeting_id: str,
        mapping: SpeakerMapping
    ) -> None:
        """
        Create a speaker mapping for a meeting.

        Args:
            meeting_id: Meeting ID
            mapping: SpeakerMapping entity
        """
        import uuid
        mapping_id = str(uuid.uuid4())

        self.execute(
            "INSERT INTO speaker_mappings (id, meeting_id, speaker_id, custom_name) VALUES (?, ?, ?, ?)",
            (mapping_id, meeting_id, mapping.speaker_id, mapping.custom_name)
        )
        self.commit()

    def get_speaker_mappings(self, meeting_id: str) -> List[SpeakerMapping]:
        """
        Retrieve all speaker mappings for a meeting.

        Args:
            meeting_id: Meeting ID

        Returns:
            List of SpeakerMapping entities
        """
        rows = self.fetch_all(
            "SELECT speaker_id, custom_name FROM speaker_mappings WHERE meeting_id = ?",
            (meeting_id,)
        )
        return [SpeakerMapping(speaker_id=row[0], custom_name=row[1]) for row in rows]

    def update_speaker_mapping(
        self,
        meeting_id: str,
        mapping: SpeakerMapping
    ) -> None:
        """
        Update a speaker mapping for a meeting.

        Args:
            meeting_id: Meeting ID
            mapping: SpeakerMapping entity with updated custom_name
        """
        self.execute(
            """
            UPDATE speaker_mappings SET custom_name = ?
            WHERE meeting_id = ? AND speaker_id = ?
            """,
            (mapping.custom_name, meeting_id, mapping.speaker_id)
        )
        self.commit()

    def _row_to_segment(self, row: tuple) -> TranscriptSegment:
        """Convert database row to TranscriptSegment entity."""
        (
            id_, meeting_id, speaker_id, start_time, end_time, text, created_at
        ) = row

        return TranscriptSegment(
            id=id_,
            meeting_id=meeting_id,
            speaker_id=speaker_id,
            start_time=start_time,
            end_time=end_time,
            text=text,
            created_at=datetime.fromisoformat(created_at) if created_at else None
        )
