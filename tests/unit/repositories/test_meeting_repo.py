"""Tests for MeetingRepository."""

import pytest
import sqlite3
from datetime import datetime
from internal.repositories.meeting import MeetingRepository
from internal.domain.meeting import Meeting, MeetingStatus


@pytest.fixture
def setup_db(test_db_path: str):
    """Setup test database with meetings table."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create meetings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            audio_path TEXT,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            audio_deleted_at TIMESTAMP
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at DESC)")

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def meeting_repo(setup_db: sqlite3.Connection):
    """Create MeetingRepository instance."""
    return MeetingRepository(setup_db)


def test_create_meeting(meeting_repo: MeetingRepository):
    """Test creating a new meeting."""
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.UPLOADING,
        progress=0
    )

    meeting_repo.create(meeting)

    # Verify meeting was created
    retrieved = meeting_repo.get_by_id("test-id")
    assert retrieved is not None
    assert retrieved.id == "test-id"
    assert retrieved.title == "Test Meeting"
    assert retrieved.status == MeetingStatus.UPLOADING


def test_get_by_id(meeting_repo: MeetingRepository):
    """Test retrieving meeting by ID."""
    # Create meeting
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.COMPLETED,
        progress=100
    )
    meeting_repo.create(meeting)

    # Retrieve
    retrieved = meeting_repo.get_by_id("test-id")
    assert retrieved is not None
    assert retrieved.id == "test-id"
    assert retrieved.progress == 100


def test_get_by_id_not_found(meeting_repo: MeetingRepository):
    """Test retrieving non-existent meeting returns None."""
    retrieved = meeting_repo.get_by_id("non-existent")
    assert retrieved is None


def test_update_meeting(meeting_repo: MeetingRepository):
    """Test updating meeting."""
    # Create meeting
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.UPLOADING,
        progress=0
    )
    meeting_repo.create(meeting)

    # Update
    meeting.status = MeetingStatus.TRANSCRIBING
    meeting.progress = 50
    meeting_repo.update(meeting)

    # Verify
    retrieved = meeting_repo.get_by_id("test-id")
    assert retrieved.status == MeetingStatus.TRANSCRIBING
    assert retrieved.progress == 50


def test_list_all_meetings(meeting_repo: MeetingRepository):
    """Test listing all meetings."""
    # Create multiple meetings
    for i in range(3):
        meeting = Meeting(
            id=f"meeting-{i}",
            title=f"Meeting {i}",
            original_filename=f"test{i}.mp3",
            status=MeetingStatus.COMPLETED,
            progress=100
        )
        meeting_repo.create(meeting)

    # List all
    meetings = meeting_repo.list_all()
    assert len(meetings) == 3


def test_list_by_status(meeting_repo: MeetingRepository):
    """Test listing meetings by status."""
    # Create meetings with different statuses
    meeting1 = Meeting(
        id="m1",
        title="M1",
        original_filename="test1.mp3",
        status=MeetingStatus.UPLOADING,
        progress=0
    )
    meeting2 = Meeting(
        id="m2",
        title="M2",
        original_filename="test2.mp3",
        status=MeetingStatus.COMPLETED,
        progress=100
    )
    meeting_repo.create(meeting1)
    meeting_repo.create(meeting2)

    # List by status
    uploading = meeting_repo.list_by_status(MeetingStatus.UPLOADING)
    completed = meeting_repo.list_by_status(MeetingStatus.COMPLETED)

    assert len(uploading) == 1
    assert len(completed) == 1
    assert uploading[0].id == "m1"
    assert completed[0].id == "m2"


def test_delete_meeting(meeting_repo: MeetingRepository):
    """Test deleting a meeting."""
    # Create meeting
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.COMPLETED,
        progress=100
    )
    meeting_repo.create(meeting)

    # Delete
    meeting_repo.delete("test-id")

    # Verify
    retrieved = meeting_repo.get_by_id("test-id")
    assert retrieved is None


@pytest.mark.parametrize("status,progress", [
    (MeetingStatus.UPLOADING, 0),
    (MeetingStatus.TRANSCRIBING, 50),
    (MeetingStatus.GENERATING, 75),
    (MeetingStatus.COMPLETED, 100),
])
def test_update_progress_and_status(
    meeting_repo: MeetingRepository,
    status: MeetingStatus,
    progress: int
):
    """Test updating meeting progress and status."""
    meeting = Meeting(
        id="test-id",
        title="Test",
        original_filename="test.mp3",
        status=MeetingStatus.UPLOADING,
        progress=0
    )
    meeting_repo.create(meeting)

    # Update
    meeting.status = status
    meeting.progress = progress
    meeting_repo.update(meeting)

    # Verify
    retrieved = meeting_repo.get_by_id("test-id")
    assert retrieved.status == status
    assert retrieved.progress == progress
