"""
Data Base Handler Test
"""

import os
import sqlite3

from src.data_base.data_base_handler import initialize_data_base


def test_initialize_data_base():
    """
    Test the initialization of the database.
    """
    # Create a temporary file path for the database
    db_file_path = "./tests/test_files/test_database.db"

    # Initialize the database
    initialize_data_base(str(db_file_path))

    # Check if the database file was created
    assert os.path.exists(db_file_path), "Database file should be created."

    # Connect to the database and check if the trades table exists
    conn = sqlite3.connect(str(db_file_path))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='trades'"
    )
    table_exists = cursor.fetchone() is not None

    conn.close()

    assert table_exists, "Trades table should exist in the database."
