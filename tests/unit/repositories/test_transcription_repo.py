"""Tests for TranscriptionRepository."""

import pytest
import sqlite3
from datetime import datetime
from internal.repositories.transcription import TranscriptionRepository
from internal.domain.transcription import TranscriptSegment, SpeakerMapping


@pytest.fixture
def setup_db(test_db_path: str):
    """Setup test database with transcription tables."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcript_segments (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker_id TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speaker_mappings (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker_id TEXT NOT NULL,
            custom_name TEXT,
            UNIQUE(meeting_id, speaker_id),
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def transcription_repo(setup_db: sqlite3.Connection):
    """Create TranscriptionRepository instance."""
    return TranscriptionRepository(setup_db)


def test_create_segment(transcription_repo: TranscriptionRepository):
    """Test creating a transcript segment."""
    segment = TranscriptSegment(
        id="seg-1",
        meeting_id="meeting-1",
        speaker_id="speaker_a",
        start_time=10.5,
        end_time=15.5,
        text="Hello world"
    )

    transcription_repo.create_segment(segment)

    # Verify
    retrieved = transcription_repo.get_segments_by_meeting("meeting-1")
    assert len(retrieved) == 1
    assert retrieved[0].text == "Hello world"


def test_get_segments_by_meeting(transcription_repo: TranscriptionRepository):
    """Test retrieving all segments for a meeting."""
    # Create segments
    for i in range(3):
        segment = TranscriptSegment(
            id=f"seg-{i}",
            meeting_id="meeting-1",
            speaker_id="speaker_a",
            start_time=float(i * 10),
            end_time=float(i * 10 + 5),
            text=f"Segment {i}"
        )
        transcription_repo.create_segment(segment)

    # Retrieve
    segments = transcription_repo.get_segments_by_meeting("meeting-1")
    assert len(segments) == 3


def test_create_speaker_mapping(transcription_repo: TranscriptionRepository):
    """Test creating speaker mapping."""
    mapping = SpeakerMapping(
        speaker_id="speaker_a",
        custom_name="张三"
    )

    transcription_repo.create_speaker_mapping("meeting-1", mapping)

    # Verify
    mappings = transcription_repo.get_speaker_mappings("meeting-1")
    assert len(mappings) == 1
    assert mappings[0].custom_name == "张三"


def test_update_speaker_mapping(transcription_repo: TranscriptionRepository):
    """Test updating speaker mapping."""
    # Create mapping
    mapping = SpeakerMapping(speaker_id="speaker_a", custom_name="张三")
    transcription_repo.create_speaker_mapping("meeting-1", mapping)

    # Update
    updated = SpeakerMapping(speaker_id="speaker_a", custom_name="李四")
    transcription_repo.update_speaker_mapping("meeting-1", updated)

    # Verify
    mappings = transcription_repo.get_speaker_mappings("meeting-1")
    assert mappings[0].custom_name == "李四"


def test_delete_segments_by_meeting(transcription_repo: TranscriptionRepository):
    """Test deleting all segments for a meeting."""
    # Create segments
    for i in range(3):
        segment = TranscriptSegment(
            id=f"seg-{i}",
            meeting_id="meeting-1",
            speaker_id="speaker_a",
            start_time=float(i * 10),
            end_time=float(i * 10 + 5),
            text=f"Segment {i}"
        )
        transcription_repo.create_segment(segment)

    # Delete
    transcription_repo.delete_segments_by_meeting("meeting-1")

    # Verify
    segments = transcription_repo.get_segments_by_meeting("meeting-1")
    assert len(segments) == 0
