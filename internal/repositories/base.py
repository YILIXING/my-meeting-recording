"""Base repository class."""

import sqlite3
from typing import Optional, List, Any, Tuple


class BaseRepository:
    """Base repository providing common database operations."""

    def __init__(self, conn: sqlite3.Connection):
        """
        Initialize repository with database connection.

        Args:
            conn: SQLite database connection
        """
        self.conn = conn

    def execute(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> sqlite3.Cursor:
        """
        Execute a SQL statement.

        Args:
            sql: SQL statement to execute
            params: Optional parameters for the SQL statement

        Returns:
            Cursor object
        """
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor

    def fetch_one(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[Tuple[Any, ...]]:
        """
        Fetch a single row from the database.

        Args:
            sql: SQL query to execute
            params: Optional parameters for the SQL query

        Returns:
            Tuple representing the row, or None if no results
        """
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        return cursor.fetchone()

    def fetch_all(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> List[Tuple[Any, ...]]:
        """
        Fetch all rows from the database.

        Args:
            sql: SQL query to execute
            params: Optional parameters for the SQL query

        Returns:
            List of tuples representing the rows
        """
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        return cursor.fetchall()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.conn.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.conn.rollback()
