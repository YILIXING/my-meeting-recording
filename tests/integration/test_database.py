"""Database integration tests."""

import pytest
import sqlite3
from pathlib import Path


@pytest.fixture
def migrate_script():
    """Import the migrate script."""
    import sys
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root / "scripts"))
    from migrate import apply_migrations
    # Return both function and migrations directory
    migrations_dir = str(project_root / "migrations")
    return apply_migrations, migrations_dir


def test_database_initialization(test_db_path: str, migrate_script):
    """Test that database can be initialized with migrations."""
    # Apply migrations
    apply_migrations, migrations_dir = migrate_script
    apply_migrations(test_db_path, migrations_dir=migrations_dir)

    # Verify tables were created
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Check meetings table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meetings'")
    assert cursor.fetchone() is not None, "meetings table should exist"

    # Check transcript_segments table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transcript_segments'")
    assert cursor.fetchone() is not None, "transcript_segments table should exist"

    # Check speaker_mappings table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='speaker_mappings'")
    assert cursor.fetchone() is not None, "speaker_mappings table should exist"

    # Check summaries table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='summaries'")
    assert cursor.fetchone() is not None, "summaries table should exist"

    # Check templates table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='templates'")
    assert cursor.fetchone() is not None, "templates table should exist"

    # Check migration log table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_migration_log'")
    assert cursor.fetchone() is not None, "_migration_log table should exist"

    conn.close()


def test_meetings_table_structure(test_db_path: str, migrate_script):
    """Test meetings table has correct structure."""
    apply_migrations, migrations_dir = migrate_script
    apply_migrations(test_db_path, migrations_dir=migrations_dir)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Check columns
    cursor.execute("PRAGMA table_info(meetings)")
    columns = {row[1] for row in cursor.fetchall()}

    required_columns = {
        "id", "title", "original_filename", "audio_path",
        "status", "progress", "error_message",
        "created_at", "updated_at", "audio_deleted_at"
    }
    assert required_columns.issubset(columns), f"meetings table missing columns: {required_columns - columns}"

    conn.close()


def test_indexes_created(test_db_path: str, migrate_script):
    """Test that indexes were created."""
    apply_migrations, migrations_dir = migrate_script
    apply_migrations(test_db_path, migrations_dir=migrations_dir)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Check meetings indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='meetings'")
    indexes = {row[0] for row in cursor.fetchall()}
    assert "idx_meetings_status" in indexes
    assert "idx_meetings_created_at" in indexes

    conn.close()


def test_migration_log_tracks_applied_migrations(test_db_path: str, migrate_script):
    """Test that migration log tracks applied migrations."""
    apply_migrations, migrations_dir = migrate_script
    apply_migrations(test_db_path, migrations_dir=migrations_dir)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Check migration was logged
    cursor.execute("SELECT version, name FROM _migration_log")
    migrations = cursor.fetchall()

    assert len(migrations) > 0, "At least one migration should be logged"

    conn.close()


def test_idempotent_migrations(test_db_path: str, migrate_script):
    """Test that running migrations twice is idempotent."""
    apply_migrations, migrations_dir = migrate_script
    # First run
    apply_migrations(test_db_path, migrations_dir=migrations_dir)

    # Second run should not fail
    apply_migrations(test_db_path, migrations_dir=migrations_dir)

    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Check migration was only logged once
    cursor.execute("SELECT COUNT(*) FROM _migration_log")
    count = cursor.fetchone()[0]

    assert count == 1, "Migration should only be applied once"

    conn.close()
