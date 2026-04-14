"""Custom exceptions for meeting application."""


class MeetingError(Exception):
    """Base exception for meeting-related errors."""
    pass


class AudioUploadError(MeetingError):
    """Raised when audio file upload fails."""
    pass


class TranscriptionError(MeetingError):
    """Raised when transcription fails."""
    pass


class SummaryGenerationError(MeetingError):
    """Raised when summary generation fails."""
    pass


class LLMConfigError(MeetingError):
    """Raised when LLM configuration is invalid."""
    pass
