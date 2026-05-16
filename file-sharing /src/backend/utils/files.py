import os
import secrets
import aiofiles
import hashlib

from pathlib import Path
from datetime import datetime, timedelta
from src.backend.utils.database import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

UPLOAD_DIR = BASE_DIR / "uploads/files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

async def save_file(file, expiration_hours=1, password=None, burn=False):
    file_id = secrets.token_urlsafe(8)

    extension = Path(file.filename).suffix
    stored_file_name = f"{file_id}{extension}"

    file_path = UPLOAD_DIR / stored_file_name

    async with aiofiles.open(file_path, "wb") as f:
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
        INSERT INTO files (id, filename, original_name, mimetype, size, created_at, expires_at, password_hash, burn)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (file_id, stored_file_name, file.filename, file.content_type, len(contents), datetime.utcnow().isoformat(), expires_at, password_hash, burn))
    conn.commit()
    conn.close()
    return file_id


def load_file(file_id, password=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files WHERE id = ?",(file_id,))
    file = cursor.fetchone()
    conn.close()

    if file is None:
        return None, "not found"

    if file["expires_at"]:
        if datetime.utcnow() > datetime.fromisoformat(file["expires_at"]):
            return None, "expired"

    if file["password_hash"]:
        if (
            not password
            or hashlib.sha256(password.encode()).hexdigest()
            != file["password_hash"]
        ):
            return None, "wrong password"

    return file, None