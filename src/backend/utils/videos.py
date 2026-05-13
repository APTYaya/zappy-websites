import json
import os
import secrets
import aiofiles
import hashlib

from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DB_PATH = BASE_DIR / "src/backend/data/videos_db.json"

UPLOAD_DIR = BASE_DIR / "uploads/videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as video:
                data = json.load(video)

                if isinstance(data, dict):
                    return data

        except json.JSONDecodeError:
            pass

    return {}


def save_db(video_db):
    with open(DB_PATH, "w") as video:
        json.dump(video_db, video, indent=2)


async def save_video(file, expiration_hours=1, password=None, burn=False):
    video_id = secrets.token_urlsafe(8)

    extension = Path(file.filename).suffix
    stored_video_name = f"{video_id}{extension}"

    video_path = UPLOAD_DIR / stored_video_name

    async with aiofiles.open(video_path, "wb") as f:
        contents = await file.read()
        await f.write(contents)

    video_db = load_db()

    expires_at = None

    if expiration_hours:
        expires_at = (
            datetime.utcnow() + timedelta(hours=expiration_hours)
        ).isoformat()

    password_hash = None

    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    video_db[video_id] = {
        "original_name": file.filename,
        "stored_video_name": stored_video_name,
        "content_type": file.content_type,
        "size": len(contents),
        "expires_at": expires_at,
        "password_hash": password_hash,
        "burn": burn,
    }

    save_db(video_db)

    return video_id


def load_video(video_id, password=None):
    video_db = load_db()

    video = video_db.get(video_id)

    if video is None:
        return None, "not found"

    if video.get("expires_at"):
        if datetime.utcnow() > datetime.fromisoformat(video["expires_at"]):
            return None, "expired"

    if video.get("password_hash"):
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