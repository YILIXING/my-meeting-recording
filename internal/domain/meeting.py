"""Meeting domain model."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class MeetingStatus(Enum):
    """Meeting processing status."""
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Meeting:
    """Meeting entity representing a recorded meeting session."""

    id: str                          # UUID
    title: str                       # Meeting title (initially timestamp)
    original_filename: str           # Original uploaded filename
    audio_path: Optional[str] = None  # Path to stored audio file
    status: MeetingStatus = MeetingStatus.UPLOADING  # Current status
    progress: int = 0                # Progress percentage (0-100)
    error_message: Optional[str] = None  # Error message if failed
    created_at: Optional[datetime] = None      # Creation time
    updated_at: Optional[datetime] = None      # Last update time
    audio_deleted_at: Optional[datetime] = None  # Audio deletion time

    def is_audio_available(self) -> bool:
        """Check if audio file is available for this meeting."""
        return self.audio_path is not None and self.audio_deleted_at is None

    def can_generate_summary(self) -> bool:
        """Check if summary can be generated for this meeting."""
        return self.status == MeetingStatus.COMPLETED

    def can_delete_audio(self) -> bool:
        """Check if audio file can be deleted."""
        return self.is_audio_available() and self.status == MeetingStatus.COMPLETED
