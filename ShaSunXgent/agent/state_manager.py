"""
The State Manager module for the Automated Content Agent.

This module handles the agent's "memory" by interacting with a persistent
database (SQLite) to track the status of processed items.
"""

import sqlite3
from pathlib import Path

class StateManager:
    """Manages the persistent state of the agent."""

    def __init__(self, db_path: str):
        """
        Initializes the StateManager and ensures the database and table exist.

        Args:
            db_path: The path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_db_and_table_exist()
        print(f"State Manager: Initialized with database at '{db_path}'.")

    def _ensure_db_and_table_exist(self):
        """Creates the database and the 'processed_items' table if they don't exist."""
        if not Path(self.db_path).parent.exists():
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_items (
                item_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def is_processed(self, item_id: str) -> bool:
        """
        Checks if an item has already been successfully processed.

        Args:
            item_id: The unique identifier of the item (e.g., video ID or article URL).

        Returns:
            True if the item exists with a 'published' status, False otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM processed_items WHERE item_id = ? AND status = 'published'", (item_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def mark_as_processed(self, item_id: str, source: str, status: str = 'published'):
        """
        Records an item in the database with a given status.

        Args:
            item_id: The unique identifier of the item.
            source: The source of the item (e.g., 'youtube', 'fastbull').
            status: The status to record (e.g., 'fetched', 'published').
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO processed_items (item_id, source, status)
            VALUES (?, ?, ?)
        """, (item_id, source, status))
        conn.commit()
        conn.close()
        print(f"State Manager: Marked item '{item_id}' as '{status}'.")

