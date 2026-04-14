"""Database migration script."""

import sqlite3
import re
from pathlib import Path
from typing import Optional


def apply_migrations(db_path: str, migrations_dir: Optional[str] = None) -> None:
    """
    Apply pending database migrations.

    Args:
        db_path: Path to the SQLite database file
        migrations_dir: Directory containing migration SQL files (default: "migrations")
    """
    if migrations_dir is None:
        migrations_dir = "migrations"

    migrations_path = Path(migrations_dir)
    if not migrations_path.exists():
        raise FileNotFoundError(f"Migrations directory not found: {migrations_dir}")

    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create migration log table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _migration_log (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get applied migrations
        cursor.execute("SELECT version FROM _migration_log")
        applied = {row[0] for row in cursor.fetchall()}

        # Find and apply new migrations
        migration_files = sorted(migrations_path.glob("*.sql"), key=lambda x: x.name)

        if not migration_files:
            print("No migration files found")
            return

        for migration_file in migration_files:
            # Extract version number from filename (e.g., "001_init_schema.sql" -> 1)
            match = re.match(r'(\d+)_', migration_file.name)
            if not match:
                print(f"Skipping invalid migration file: {migration_file.name}")
                continue

            version = int(match.group(1))

            if version not in applied:
                print(f"Applying migration: {migration_file.name}")
                sql = migration_file.read_text()

                # Execute the migration
                cursor.executescript(sql)

                # Log the migration
                cursor.execute(
                    "INSERT INTO _migration_log (version, name) VALUES (?, ?)",
                    (version, migration_file.name)
                )

                conn.commit()
                print(f"Successfully applied migration {version}: {migration_file.name}")
            else:
                print(f"Migration {version} already applied, skipping")

    except Exception as err:
        conn.rollback()
        raise ValueError(f"Migration failed: {err}") from err
    finally:
        conn.close()


def main():
    """Command-line interface for running migrations."""
    import argparse

    parser = argparse.ArgumentParser(description="Apply database migrations")
    parser.add_argument(
        "--db-path",
        default="data/meetings.db",
        help="Path to the database file (default: data/meetings.db)"
    )
    parser.add_argument(
        "--migrations-dir",
        default="migrations",
        help="Directory containing migration files (default: migrations)"
    )

    args = parser.parse_args()

    try:
        apply_migrations(args.db_path, args.migrations_dir)
        print("All migrations applied successfully")
    except Exception as err:
        print(f"Error: {err}")
        exit(1)


if __name__ == "__main__":
    main()
