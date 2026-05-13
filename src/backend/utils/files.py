import json
import os
import secrets
import aiofiles
import hashlib

from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DB_PATH = BASE_DIR / "src/backend/data/files_db.json"

UPLOAD_DIR = BASE_DIR / "uploads/files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def load_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as file:
                data = json.load(file)

                if isinstance(data, dict):
                    return data

        except json.JSONDecodeError:
            pass

    return {}


def save_db(file_db):
    with open(DB_PATH, "w") as file:
        json.dump(file_db, file, indent=2)


async def save_file(file, expiration_hours=1, password=None, burn=False):
    file_id = secrets.token_urlsafe(8)

    extension = Path(file.filename).suffix
    stored_file_name = f"{file_id}{extension}"

    file_path = UPLOAD_DIR / stored_file_name

    async with aiofiles.open(file_path, "wb") as f:
        contents = await file.read()
        await f.write(contents)

    file_db = load_db()

    expires_at = None

    if expiration_hours:
        expires_at = (
            datetime.utcnow() + timedelta(hours=expiration_hours)
        ).isoformat()

    password_hash = None

    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    file_db[file_id] = {
        "original_name": file.filename,
        "stored_file_name": stored_file_name,
        "content_type": file.content_type,
        "size": len(contents),
        "expires_at": expires_at,
        "password_hash": password_hash,
        "burn": burn,
    }

    save_db(file_db)

    return file_id


def load_file(file_id, password=None):
    file_db = load_db()

    file = file_db.get(file_id)

    if file is None:
        return None, "not found"

    if file.get("expires_at"):
        if datetime.utcnow() > datetime.fromisoformat(file["expires_at"]):
            return None, "expired"

    if file.get("password_hash"):
        if (
            not password
            or hashlib.sha256(password.encode()).hexdigest()
            != file["password_hash"]
        ):
            return None, "wrong password"

    return file, None