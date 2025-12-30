"""
Database management for Sentiment Space.
Handles SQLite connections and schema initialization.
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime


class Database:
    """SQLite database manager for persistent thought storage."""

    def __init__(self, db_path: str = "sentiment.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory()
        self._init_schema()

    def _ensure_directory(self) -> None:
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _init_schema(self) -> None:
        """Initialize database schema on first run."""
        schema_path = os.path.join(
            os.path.dirname(__file__), "schema.sql"
        )
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        with open(schema_path, "r") as f:
            schema = f.read()

        with self._get_connection() as conn:
            conn.executescript(schema)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def insert_thought(
        self,
        raw_text: str,
        summary: Optional[str] = None,
        sentiment: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> int:
        """
        Insert a new thought into the database.

        Args:
            raw_text: Original user input
            summary: AI-generated summary
            sentiment: Sentiment classification (positive/neutral/negative)
            confidence: Confidence score (0-1)

        Returns:
            ID of inserted record
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO thoughts (raw_text, summary, sentiment, confidence)
                VALUES (?, ?, ?, ?)
                """,
                (raw_text, summary, sentiment, confidence),
            )
            conn.commit()
            return cursor.lastrowid

    def get_thought(self, thought_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single thought by ID.

        Args:
            thought_id: ID of the thought

        Returns:
            Dictionary with thought data or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM thoughts WHERE id = ?", (thought_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_thoughts(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all thoughts with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of thought dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM thoughts
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_thoughts_by_sentiment(self, sentiment: str) -> List[Dict[str, Any]]:
        """
        Retrieve thoughts filtered by sentiment.

        Args:
            sentiment: Sentiment type (positive/neutral/negative)

        Returns:
            List of matching thought dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM thoughts
                WHERE sentiment = ?
                ORDER BY created_at DESC
                """,
                (sentiment,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_thought(
        self,
        thought_id: int,
        summary: Optional[str] = None,
        sentiment: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> bool:
        """
        Update an existing thought.

        Args:
            thought_id: ID of the thought
            summary: Updated summary
            sentiment: Updated sentiment
            confidence: Updated confidence score

        Returns:
            True if update successful, False if thought not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE thoughts
                SET summary = COALESCE(?, summary),
                    sentiment = COALESCE(?, sentiment),
                    confidence = COALESCE(?, confidence),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (summary, sentiment, confidence, thought_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_thought(self, thought_id: int) -> bool:
        """
        Delete a thought from the database.

        Args:
            thought_id: ID of the thought to delete

        Returns:
            True if deletion successful, False if thought not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM thoughts WHERE id = ?", (thought_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with count and sentiment distribution
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute("SELECT COUNT(*) FROM thoughts")
            total = cursor.fetchone()[0]

            # Sentiment distribution
            cursor.execute(
                """
                SELECT sentiment, COUNT(*) as count
                FROM thoughts
                GROUP BY sentiment
                """
            )
            sentiment_dist = {row[0]: row[1] for row in cursor.fetchall()}

            return {"total": total, "sentiment_distribution": sentiment_dist}
