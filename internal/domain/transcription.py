"""Transcription domain model."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TranscriptSegment:
    """A single segment of transcribed audio with speaker identification."""

    id: str                          # UUID
    meeting_id: str                  # Associated meeting ID
    speaker_id: str                  # Speaker ID (e.g., "speaker_a")
    start_time: float                # Start time in seconds
    end_time: float                  # End time in seconds
    text: str                        # Transcribed text content
    created_at: Optional[datetime] = None  # Creation timestamp

    def format_timestamp(self) -> str:
        """
        Format start time as HH:MM:SS.

        Returns:
            str: Formatted timestamp
        """
        hours = int(self.start_time // 3600)
        minutes = int((self.start_time % 3600) // 60)
        seconds = int(self.start_time % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass
class SpeakerMapping:
    """Mapping between speaker IDs and custom names."""

    speaker_id: str                  # Original ID (e.g., "speaker_a")
    custom_name: Optional[str] = None  # Custom name (e.g., "张三")

    def display_name(self) -> str:
        """
        Get the display name for this speaker.

        Returns:
            str: Custom name if set, otherwise formatted speaker ID
        """
        if self.custom_name:
            return self.custom_name
        # Convert "speaker_a" to "Speaker A"
        return self.speaker_id.replace("_", " ").title()
