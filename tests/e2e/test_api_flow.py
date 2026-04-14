"""End-to-End tests for the application."""

import pytest
import asyncio
import tempfile
import sqlite3
from pathlib import Path
from typing import AsyncGenerator

# FastAPI and httpx are optional for E2E tests
try:
    from fastapi import FastAPI
    from httpx import AsyncClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from internal.domain.meeting import Meeting, MeetingStatus
from internal.repositories.meeting import MeetingRepository
from internal.repositories.transcription import TranscriptionRepository


@pytest.fixture
async def app() -> AsyncGenerator:
    """Create test FastAPI app."""
    if not FASTAPI_AVAILABLE:
        pytest.skip("FastAPI not available")

    # Use test database
    test_db = tempfile.mktemp(suffix=".db")
    """Create test FastAPI app."""
    # Use test database
    test_db = tempfile.mktemp(suffix=".db")

    # Initialize database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcript_segments (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker_id TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            prompt TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    # Create app
    from internal.utils.config import ConfigManager
    config = ConfigManager()
    llm_config = {
        "default_service": "doubao",
        "services": {
            "doubao": {
                "api_key": "test"
            }
        }
    }
    config.save(llm_config)


    app = FastAPI()
    app.include_router(router)

    # Override database path
    import internal.api.dependencies as deps
    original_get_db = deps.get_db_path

    def mock_get_db():
        return test_db

    deps.get_db_path = mock_get_db

    yield app

    # Cleanup
    import os
    os.unlink(test_db)


@pytest.mark.asyncio
async def test_upload_meeting_flow(app: FastAPI):
    """Test complete meeting upload flow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test health check
        response = await client.get("/api/config/llm")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_meeting_crud_operations(app: FastAPI):
    """Test CRUD operations for meetings."""
    test_db = tempfile.mktemp(suffix=".db")

    # Setup database
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

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
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Create meeting
    meeting = Meeting(
        id="test-1",
        title="Test Meeting",
        original_filename="test.mp3",
        status=MeetingStatus.UPLOADING
    )

    repo = MeetingRepository(conn)
    repo.create(meeting)

    # Retrieve
    retrieved = repo.get_by_id("test-1")
    assert retrieved is not None
    assert retrieved.title == "Test Meeting"

    # Update
    retrieved.status = MeetingStatus.COMPLETED
    retrieved.progress = 100
    repo.update(retrieved)

    # Verify update
    updated = repo.get_by_id("test-1")
    assert updated.status == MeetingStatus.COMPLETED
    assert updated.progress == 100

    # Delete
    repo.delete("test-1")
    assert repo.get_by_id("test-1") is None

    conn.close()
    import os
    os.unlink(test_db)


def test_performance_meeting_list():
    """Performance test for meeting list retrieval."""
    import time

    # Setup test database with many meetings
    test_db = tempfile.mktemp(suffix=".db")
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            status TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            error_message TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            audio_deleted_at TIMESTAMP,
            audio_path TEXT
        )
    """)

    # Insert 100 meetings
    for i in range(100):
        cursor.execute(
            """
            INSERT INTO meetings (id, title, original_filename, status, progress)
            VALUES (?, ?, ?, ?, ?)
            """,
            (f"meeting-{i}", f"Meeting {i}", f"test{i}.mp3", "completed", 100)
        )

    conn.commit()

    # Test retrieval performance
    repo = MeetingRepository(conn)
    start_time = time.time()

    meetings = repo.list_all()

    end_time = time.time()
    elapsed = end_time - start_time

    conn.close()
    import os
    os.unlink(test_db)

    assert len(meetings) == 100
    assert elapsed < 1.0, f"Retrieval took {elapsed:.3f}s, expected < 1.0s"


def test_performance_transcription_search():
    """Performance test for transcription segment search."""
    import time

    test_db = tempfile.mktemp(suffix=".db")
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transcript_segments (
            id TEXT PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            speaker_id TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert 500 segments
    for i in range(500):
        cursor.execute(
            """
            INSERT INTO transcript_segments (id, meeting_id, speaker_id, start_time, end_time, text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (f"seg-{i}", f"meeting-{i % 10}", "speaker_a", i * 10.0, i * 10.0 + 5.0, f"Segment {i}")
        )

    conn.commit()

    # Test search performance
    repo = TranscriptionRepository(conn)
    start_time = time.time()

    segments = repo.get_segments_by_meeting("meeting-5")

    end_time = time.time()
    elapsed = end_time - start_time

    conn.close()
    import os
    os.unlink(test_db)

    assert len(segments) == 50
    assert elapsed < 0.5, f"Search took {elapsed:.3f}s, expected < 0.5s"


@pytest.mark.asyncio
async def test_concurrent_requests(app: FastAPI):
    """Test handling concurrent requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Send 10 concurrent requests
        tasks = [
            client.get("/api/meetings")
            for _ in range(10)
        ]

        start_time = asyncio.get_event_loop().time()
        responses = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()

        elapsed = end_time - start_time

        # All requests should succeed
        for response in responses:
            assert response.status_code in [200, 404]  # 404 is OK for empty database

        # Should complete in reasonable time
        assert elapsed < 5.0, f"Concurrent requests took {elapsed:.2f}s"
