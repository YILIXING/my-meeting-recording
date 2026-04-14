"""API dependencies for dependency injection."""

import sqlite3
from fastapi import Depends
from typing import Generator
from pathlib import Path

from internal.repositories.meeting import MeetingRepository
from internal.repositories.transcription import TranscriptionRepository
from internal.repositories.summary import SummaryRepository
from internal.repositories.template import TemplateRepository
from internal.services.audio_processor import AudioProcessor
from internal.services.llm_transcriber import LLMTranscriber
from internal.services.llm_summarizer import LLMSummarizer
from internal.llm.base import LLMService
from internal.llm.factory import create_llm_service


def get_db_path() -> str:
    """Get database path from config."""
    return "data/meetings.db"


def get_db(db_path: str = Depends(get_db_path)) -> Generator[sqlite3.Connection, None, None]:
    """
    Get database connection.

    Args:
        db_path: Path to database file

    Yields:
        sqlite3.Connection: Database connection
    """
    # Ensure database directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_llm_service() -> LLMService:
    """
    Get LLM service instance.

    Returns:
        LLMService: Configured LLM service
    """
    return create_llm_service()


def get_meeting_repo(
    db: sqlite3.Connection = Depends(get_db)
) -> MeetingRepository:
    """Get meeting repository."""
    return MeetingRepository(db)


def get_transcription_repo(
    db: sqlite3.Connection = Depends(get_db)
) -> TranscriptionRepository:
    """Get transcription repository."""
    return TranscriptionRepository(db)


def get_summary_repo(
    db: sqlite3.Connection = Depends(get_db)
) -> SummaryRepository:
    """Get summary repository."""
    return SummaryRepository(db)


def get_template_repo(
    db: sqlite3.Connection = Depends(get_db)
) -> TemplateRepository:
    """Get template repository."""
    return TemplateRepository(db)


def get_audio_processor() -> AudioProcessor:
    """Get audio processor service."""
    return AudioProcessor()


def get_transcriber(
    meeting_repo: MeetingRepository = Depends(get_meeting_repo),
    transcription_repo: TranscriptionRepository = Depends(get_transcription_repo),
    llm_service: LLMService = Depends(get_llm_service)
) -> LLMTranscriber:
    """Get LLM transcriber service."""
    return LLMTranscriber(meeting_repo, transcription_repo, llm_service)


def get_summarizer(
    summary_repo: SummaryRepository = Depends(get_summary_repo),
    transcription_repo: TranscriptionRepository = Depends(get_transcription_repo),
    meeting_repo: MeetingRepository = Depends(get_meeting_repo),
    llm_service: LLMService = Depends(get_llm_service)
) -> LLMSummarizer:
    """Get LLM summarizer service."""
    return LLMSummarizer(summary_repo, transcription_repo, meeting_repo, llm_service)
