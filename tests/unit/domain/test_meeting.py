"""Tests for Meeting domain model."""

import pytest
from datetime import datetime
from internal.domain.meeting import Meeting, MeetingStatus


@pytest.mark.parametrize("status,can_generate", [
    (MeetingStatus.UPLOADING, False),
    (MeetingStatus.TRANSCRIBING, False),
    (MeetingStatus.GENERATING, False),
    (MeetingStatus.COMPLETED, True),
    (MeetingStatus.FAILED, False),
    (MeetingStatus.CANCELLED, False),
])
def test_meeting_can_generate_summary(status: MeetingStatus, can_generate: bool):
    """Test that only completed meetings can generate summaries."""
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=status,
        progress=0
    )
    assert meeting.can_generate_summary() == can_generate


def test_meeting_is_audio_available():
    """Test audio availability check."""
    # Meeting with audio and not deleted
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.COMPLETED,
        audio_path="/path/to/audio.mp3",
        progress=100
    )
    assert meeting.is_audio_available() is True

    # Meeting with audio but deleted
    meeting.audio_deleted_at = datetime.now()
    assert meeting.is_audio_available() is False

    # Meeting without audio path
    meeting.audio_path = None
    meeting.audio_deleted_at = None
    assert meeting.is_audio_available() is False


def test_meeting_can_delete_audio():
    """Test audio deletion eligibility."""
    # Completed meeting with audio can delete
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.COMPLETED,
        audio_path="/path/to/audio.mp3",
        progress=100
    )
    assert meeting.can_delete_audio() is True

    # Meeting without audio cannot delete
    meeting.audio_path = None
    assert meeting.can_delete_audio() is False

    # Non-completed meeting cannot delete
    meeting.audio_path = "/path/to/audio.mp3"
    meeting.status = MeetingStatus.TRANSCRIBING
    assert meeting.can_delete_audio() is False


@pytest.mark.parametrize("initial_title", [
    "2026-04-14 14:00会议",
    "2026-04-15 10:00会议",
])
def test_meeting_initial_title_format(initial_title: str):
    """Test that meeting can be created with timestamp title."""
    meeting = Meeting(
        id="test-id",
        title=initial_title,
        original_filename="test.mp3",
        status=MeetingStatus.UPLOADING,
        progress=0
    )
    assert meeting.title == initial_title


def test_meeting_progress_bounds():
    """Test that progress is within 0-100 range."""
    meeting = Meeting(
        id="test-id",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.TRANSCRIBING,
        progress=50
    )
    assert 0 <= meeting.progress <= 100

    # Test progress at boundaries
    meeting.progress = 0
    assert meeting.progress == 0

    meeting.progress = 100
    assert meeting.progress == 100
