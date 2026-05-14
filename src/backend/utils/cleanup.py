from src.backend.utils.database import get_connection
from src.backend.utils.files import UPLOAD_DIR as FILE_UPLOAD_DIR
from src.backend.utils.videos import UPLOAD_DIR as VIDEO_UPLOAD_DIR
import os
import shutil
import threading
import time
from datetime import datetime, timedelta


def delete_paste(paste_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pastes WHERE id = ?", (paste_id,))
    conn.commit()
    conn.close()

def delete_file(file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    file = cursor.fetchone()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()

    file_path = FILE_UPLOAD_DIR / file["filename"]
    if os.path.exists(file_path):
        os.remove(file_path)


def delete_video(video_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    file = cursor.fetchone()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
    conn.commit()
    conn.close()

    file_path = VIDEO_UPLOAD_DIR / file["filename"]
    if os.path.exists(file_path):
        os.remove(file_path)

def cleanup_temp_uploads():
    temp_dir = "uploads/temp"
    if not os.path.exists(temp_dir):
        return
    for upload_id in os.listdir(temp_dir):
        folder = os.path.join(temp_dir, upload_id)
        age = datetime.utcnow() - datetime.fromtimestamp(os.path.getmtime(folder))
        if age > timedelta(hours=24):
            shutil.rmtree(folder)

def cleanup_expired():
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow().isoformat()

    cursor.execute("SELECT id FROM files WHERE expires_at <= ?", (now,))
    for row in cursor.fetchall():
        delete_file(row["id"])

    cursor.execute("SELECT id FROM videos WHERE expires_at <= ?", (now,))
    for row in cursor.fetchall():
        delete_video(row["id"])

    cursor.execute("SELECT id FROM pastes WHERE expires_at <= ?", (now,))
    for row in cursor.fetchall():
        delete_paste(row["id"])

    conn.close()


def cleanup_loop():
    while True:
        try:
            cleanup_expired()
            cleanup_temp_uploads()
        except Exception as e:
            print(f"Cleanup error: {e}")

        time.sleep(300) 