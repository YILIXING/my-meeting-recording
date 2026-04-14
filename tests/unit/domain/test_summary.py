"""Tests for Summary domain model."""

import pytest
from datetime import datetime
from internal.domain.summary import Summary


def test_summary_creation():
    """Test summary can be created with all fields."""
    now = datetime.now()
    summary = Summary(
        id="test-id",
        meeting_id="test-meeting",
        version=1,
        prompt="Summarize the meeting",
        content="Meeting summary content",
        created_at=now
    )
    assert summary.id == "test-id"
    assert summary.meeting_id == "test-meeting"
    assert summary.version == 1
    assert summary.prompt == "Summarize the meeting"
    assert summary.content == "Meeting summary content"
    assert summary.created_at == now


def test_summary_version_increment():
    """Test that summary versions can be incremented."""
    summary1 = Summary(
        id="summary-1",
        meeting_id="test-meeting",
        version=1,
        prompt="First version",
        content="Content 1"
    )

    summary2 = Summary(
        id="summary-2",
        meeting_id="test-meeting",
        version=2,
        prompt="Second version",
        content="Content 2"
    )

    assert summary2.version > summary1.version


@pytest.mark.parametrize("version", [1, 2, 3, 10])
def test_summary_version_positive(version: int):
    """Test that summary versions are positive integers."""
    summary = Summary(
        id=f"summary-{version}",
        meeting_id="test-meeting",
        version=version,
        prompt="Test prompt",
        content="Test content"
    )
    assert summary.version >= 1


def test_summary_content_required():
    """Test that summary content is required."""
    summary = Summary(
        id="test-id",
        meeting_id="test-meeting",
        version=1,
        prompt="Test prompt",
        content="This is the summary content"
    )
    assert len(summary.content) > 0
