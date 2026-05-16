import sqlite3
import os 

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "zappy.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth(
        token TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pastes (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            language TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            password_hash TEXT,
            burn INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            mimetype TEXT NOT NULL,
            size INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            password_hash TEXT,
            burn INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            title TEXT NOT NULL,
            mimetype TEXT NOT NULL,
            size INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            password_hash TEXT,
            burn INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

def migrate_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(files)")
    file_columns = [row["name"] for row in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(videos)")
    video_columns = [row["name"] for row in cursor.fetchall()]
    
    if "last_download_at" not in file_columns:
        cursor.execute("ALTER TABLE files ADD COLUMN last_download_at TEXT")
    
    if "last_download_at" not in video_columns:
        cursor.execute("ALTER TABLE videos ADD COLUMN last_download_at TEXT")
    
    conn.commit()
    conn.close()

migrate_db()