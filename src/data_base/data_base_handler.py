"""
Data Base Handler for SQLite
This module initializes the SQLite database and creates the necessary tables for storing trade data.
"""

import logging
import os
import sqlite3

logger = logging.getLogger(__name__)


def initialize_data_base(data_base_file_path):
    """
    Initializes the SQLite database and creates the trades table if it doesn't exist.
    Args:
        data_base_file_path (str): The file path for the SQLite database.
    """
    if not os.path.exists(os.path.dirname(data_base_file_path)):
        os.makedirs(os.path.dirname(data_base_file_path), exist_ok=True)
        logger.info(
            "Created directory for file: %s", os.path.dirname(data_base_file_path)
        )

    conn = sqlite3.connect(data_base_file_path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS trades (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT,
      pair TEXT,
      type TEXT,
      entry REAL,
      stop_loss REAL,
      take_profit REAL,
      exit REAL,
      profit REAL,
      size REAL,
      leverage REAL,
      strategy TEXT,
      result TEXT,
      confidence INTEGER,
      session TEXT,
      note TEXT
    )"""
    )

    conn.commit()
    conn.close()
