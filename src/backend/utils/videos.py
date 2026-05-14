import json
import os
import secrets
import aiofiles
import hashlib

from pathlib import Path
from datetime import datetime, timedelta
from src.backend.utils.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

UPLOAD_DIR = BASE_DIR / "uploads/videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_video(file, expiration_hours=1, password=None, burn=False):
    video_id = secrets.token_urlsafe(8)

    extension = Path(file.filename).suffix
    stored_video_name = f"{video_id}{extension}"

    video_path = UPLOAD_DIR / stored_video_name

    async with aiofiles.open(video_path, "wb") as f:
        contents = await file.read()
        await f.write(contents)

    expires_at = None

    if expiration_hours:
        expires_at = (
            datetime.utcnow() + timedelta(hours=expiration_hours)
        ).isoformat()

    password_hash = None

    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO videos (id, filename, title, mimetype, size, created_at, expires_at, password_hash, burn)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (video_id, stored_video_name, file.filename, file.content_type, len(contents), datetime.utcnow().isoformat(), expires_at, password_hash, burn))
    conn.commit()
    conn.close()
    return video_id


def load_video(video_id, password=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE id = ?",(video_id,))
    video = cursor.fetchone()
    conn.close()

    if video is None:
        return None, "not found"

    if video["expires_at"]:
        if datetime.utcnow() > datetime.fromisoformat(video["expires_at"]):
            return None, "expired"

    if video["password_hash"]:
        if (
            not password
            or hashlib.sha256(password.encode()).hexdigest()
            != video["password_hash"]
        ):
            return None, "wrong password"

    return video, None


def video_streamer(file_path, start, end):
    with open(file_path, "rb") as f:
        f.seek(start)

        remaining = end - start

        while remaining > 0:
            chunk_size = min(1024 * 1024, remaining)

            data = f.read(chunk_size)

            if not data:
                break

            remaining -= len(data)

            yield data