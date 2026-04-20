import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "phases_log.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phase_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pilot_name TEXT NOT NULL,
            last_phase INTEGER NOT NULL,
            device_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()
