import os
import psycopg2
from app.config.settings import settings

def get_db_connection():
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment variables")
    return psycopg2.connect(settings.DATABASE_URL)

def init_db():
    if not settings.DATABASE_URL:
        print("DATABASE_URL is not set. Skipping DB initialization.")
        return
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phase_records (
                id SERIAL PRIMARY KEY,
                pilot_name TEXT NOT NULL,
                last_phase INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error initializing DB: {e}")

init_db()
