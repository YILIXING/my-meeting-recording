"""Tests for Repository base class."""

import pytest
import sqlite3
from internal.repositories.base import BaseRepository


@pytest.fixture
def db_conn(test_db_path: str):
    """Create a database connection for testing."""
    # Create tables
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_entities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    yield conn
    conn.close()


def test_base_repository_connection(db_conn: sqlite3.Connection):
    """Test that BaseRepository can be initialized with a connection."""
    repo = BaseRepository(db_conn)
    assert repo.conn is db_conn


def test_base_repository_execute(db_conn: sqlite3.Connection):
    """Test BaseRepository execute method."""
    repo = BaseRepository(db_conn)

    # Insert
    repo.execute(
        "INSERT INTO test_entities (id, name) VALUES (?, ?)",
        ("test-id", "Test Entity")
    )

    # Query
    cursor = repo.fetch_one(
        "SELECT * FROM test_entities WHERE id = ?",
        ("test-id",)
    )

    assert cursor is not None
    assert cursor[0] == "test-id"
    assert cursor[1] == "Test Entity"


def test_base_repository_fetch_one(db_conn: sqlite3.Connection):
    """Test fetch_one returns single row or None."""
    repo = BaseRepository(db_conn)

    # No results
    result = repo.fetch_one("SELECT * FROM test_entities WHERE id = ?", ("non-existent",))
    assert result is None

    # Insert and fetch
    repo.execute(
        "INSERT INTO test_entities (id, name) VALUES (?, ?)",
        ("test-id", "Test")
    )

    result = repo.fetch_one("SELECT * FROM test_entities WHERE id = ?", ("test-id",))
    assert result is not None
    assert result[0] == "test-id"


def test_base_repository_fetch_all(db_conn: sqlite3.Connection):
    """Test fetch_all returns all rows."""
    repo = BaseRepository(db_conn)

    # Insert multiple
    for i in range(3):
        repo.execute(
            "INSERT INTO test_entities (id, name) VALUES (?, ?)",
            (f"id-{i}", f"Entity {i}")
        )

    # Fetch all
    results = repo.fetch_all("SELECT * FROM test_entities ORDER BY id")
    assert len(results) == 3
    assert results[0][0] == "id-0"
    assert results[2][0] == "id-2"
