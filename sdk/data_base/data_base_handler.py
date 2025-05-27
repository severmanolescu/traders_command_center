import sqlite3


def initialize_data_base(data_base_file_path):
    """
    Initializes the SQLite database and creates the trades table if it doesn't exist.
    Args:
        data_base_file_path (str): The file path for the SQLite database.
    """
    conn = sqlite3.connect(data_base_file_path)
    c = conn.cursor()
    conn.execute('''CREATE TABLE IF NOT EXISTS trades (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT,
      pair TEXT,
      type TEXT,
      entry REAL,
      stopLoss REAL,
      takeProfit REAL,
      exit REAL,
      profit REAL,
      size REAL,
      leverage REAL,
      strategy TEXT,
      result TEXT,
      confidence INTEGER,
      session TEXT,
      note TEXT
    )''')

    conn.commit()
    conn.close()