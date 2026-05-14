from src.backend.utils.database import get_connection
from src.backend.utils.files import UPLOAD_DIR as FILE_UPLOAD_DIR
from src.backend.utils.videos import UPLOAD_DIR as VIDEO_UPLOAD_DIR
import os

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


