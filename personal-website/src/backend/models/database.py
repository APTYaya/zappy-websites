import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__),  "..", "data", "zappy.db" )

def get_connection ():
    conn = sqlite3.connect(DB_PATH)
    conn.Row_factory = sqlite3.row 
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS music_history(
        id TEXT PRIMARY KEY, 
        track_title TEXT NOT NULL,
        artist TEXT NOT NULL,
        album TEXT NOT NULL,
        played_at TEXT NOT NULL,
        source TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        platform TEXT NOT NULL,
        status TEXT NOT NULL,
        playtime_minutes INTEGER,
        rating TEXT,
        cover_image_url TEXT,
        steam_app_id TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        wakatime_project_name TEXT NOT NULL,
        manual_hours INTEGER,
        started_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blog_posts(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS socials(
        id TEXT PRIMARY KEY,
        platform TEXT NOT NULL,
        url TEXT NOT NULL
        )
    """)

    cursorr.execute("""
        CREATE TABLE IF NOT EXISTS videos(
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        file_path TEXT NOT NULL,
        game TEXT,
        created_at TEXT NOT NULL,
        length INTEGER,
        size INTEGER,
        mimetype TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth(
        token TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Added incase I wanna manually wipe and rebuild the database without starting the whole app
if __name__ == "__main__":
    init_db()
    print("Database initialized!")