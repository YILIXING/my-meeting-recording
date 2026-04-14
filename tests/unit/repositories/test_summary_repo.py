"""Tests for SummaryRepository."""

import pytest
import sqlite3
from datetime import datetime
from internal.repositories.summary import SummaryRepository
from internal.domain.summary import Summary


@pytest.fixture
def setup_db(test_db_path: str):
    """Setup test database with summaries table."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create summaries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def summary_repo(setup_db: sqlite3.Connection):
    """Create SummaryRepository instance."""
    return SummaryRepository(setup_db)


def test_create_summary(summary_repo: SummaryRepository):
    """Test creating a new summary."""
    summary = Summary(
        id="summary-1",
        meeting_id="meeting-1",
        version=1,
        prompt="Summarize the meeting",
        content="Meeting summary content"
    )

    summary_repo.create(summary)

    # Verify
    retrieved = summary_repo.get_by_id("summary-1")
    assert retrieved is not None
    assert retrieved.content == "Meeting summary content"


def test_get_by_meeting(summary_repo: SummaryRepository):
    """Test retrieving all summaries for a meeting."""
    # Create summaries
    for i in range(3):
        summary = Summary(
            id=f"summary-{i}",
            meeting_id="meeting-1",
            version=i + 1,
            prompt=f"Prompt {i}",
            content=f"Content {i}"
        )
        summary_repo.create(summary)

    # Retrieve
    summaries = summary_repo.get_by_meeting("meeting-1")
    assert len(summaries) == 3


def test_get_latest_version(summary_repo: SummaryRepository):
    """Test retrieving latest summary version."""
    # Create summaries
    for i in range(3):
        summary = Summary(
            id=f"summary-{i}",
            meeting_id="meeting-1",
            version=i + 1,
            prompt=f"Prompt {i}",
            content=f"Content {i}"
        )
        summary_repo.create(summary)

    # Get latest
    latest = summary_repo.get_latest_by_meeting("meeting-1")
    assert latest is not None
    assert latest.version == 3


def test_delete_summary(summary_repo: SummaryRepository):
    """Test deleting a summary."""
    summary = Summary(
        id="summary-1",
        meeting_id="meeting-1",
        version=1,
        prompt="Test",
        content="Test content"
    )
    summary_repo.create(summary)

    # Delete
    summary_repo.delete("summary-1")

    # Verify
    retrieved = summary_repo.get_by_id("summary-1")
    assert retrieved is None
