"""Summary domain model."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Summary:
    """
    Meeting summary entity.

    Represents a generated summary for a meeting, supporting multiple versions.
    """

    id: str                          # UUID
    meeting_id: str                  # Associated meeting ID
    version: int                     # Version number
    prompt: str                      # User prompt used for generation
    content: str                     # Generated summary content
    created_at: Optional[datetime] = None  # Creation timestamp
