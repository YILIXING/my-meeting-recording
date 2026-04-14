"""Tests for Transcription domain model."""

import pytest
from datetime import datetime
from typing import Optional
from internal.domain.transcription import TranscriptSegment, SpeakerMapping


@pytest.mark.parametrize("start_time,expected_timestamp", [
    (0.0, "00:00:00"),
    (59.9, "00:00:59"),
    (60.0, "00:01:00"),
    (3599.9, "00:59:59"),
    (3600.0, "01:00:00"),
    (3661.0, "01:01:01"),
])
def test_transcript_segment_format_timestamp(start_time: float, expected_timestamp: str):
    """Test timestamp formatting."""
    segment = TranscriptSegment(
        id="test-id",
        meeting_id="test-meeting",
        speaker_id="speaker_a",
        start_time=start_time,
        end_time=start_time + 5.0,
        text="Test text"
    )
    assert segment.format_timestamp() == expected_timestamp


def test_transcript_segment_fields():
    """Test transcript segment has all required fields."""
    segment = TranscriptSegment(
        id="test-id",
        meeting_id="test-meeting",
        speaker_id="speaker_a",
        start_time=10.5,
        end_time=15.5,
        text="Hello world"
    )
    assert segment.id == "test-id"
    assert segment.meeting_id == "test-meeting"
    assert segment.speaker_id == "speaker_a"
    assert segment.start_time == 10.5
    assert segment.end_time == 15.5
    assert segment.text == "Hello world"


@pytest.mark.parametrize("speaker_id,custom_name,expected_display", [
    ("speaker_a", None, "Speaker A"),
    ("speaker_b", None, "Speaker B"),
    ("speaker_a", "张三", "张三"),
    ("speaker_b", "李四", "李四"),
])
def test_speaker_mapping_display_name(speaker_id: str, custom_name: Optional[str], expected_display: str):
    """Test speaker mapping display name."""
    mapping = SpeakerMapping(
        speaker_id=speaker_id,
        custom_name=custom_name
    )
    assert mapping.display_name() == expected_display


def test_speaker_mapping_partial_custom_names():
    """Test that speakers can be partially named."""
    # With custom name
    mapping1 = SpeakerMapping(speaker_id="speaker_a", custom_name="张三")
    assert mapping1.display_name() == "张三"

    # Without custom name (fallback to default)
    mapping2 = SpeakerMapping(speaker_id="speaker_b", custom_name=None)
    assert mapping2.display_name() == "Speaker B"


@pytest.mark.parametrize("speaker_count", [3, 5, 10])
def test_multiple_speakers(speaker_count: int):
    """Test handling multiple speakers."""
    for i in range(speaker_count):
        speaker_id = f"speaker_{chr(97 + i)}"  # speaker_a, speaker_b, etc.
        mapping = SpeakerMapping(speaker_id=speaker_id, custom_name=None)
        assert mapping.display_name() == f"Speaker {chr(65 + i)}"
