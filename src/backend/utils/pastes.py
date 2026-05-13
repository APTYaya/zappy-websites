import json
import os
import secrets
import hashlib

from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

DB_PATH = BASE_DIR / "src/backend/data/pastes_db.json"


def load_db():
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r") as text:
                data = json.load(text)

                if isinstance(data, dict):
                    return data

        except json.JSONDecodeError:
            pass

    return {}


def save_db(paste_db):
    with open(DB_PATH, "w") as text:
        json.dump(paste_db, text, indent=2)


def save_paste(content, language, expiration_hours=1, password=None, burn=False):
    paste_id = secrets.token_urlsafe(8)

    paste_db = load_db()

    expires_at = None

    if expiration_hours:
        expires_at = (
            datetime.utcnow() + timedelta(hours=expiration_hours)
        ).isoformat()

    password_hash = None

    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    paste_db[paste_id] = {
        "content": content,
        "language": language,
        "expires_at": expires_at,
        "password_hash": password_hash,
        "burn": burn,
    }

    save_db(paste_db)

    return paste_id


def load_paste(paste_id, password=None):
    paste_db = load_db()

    paste = paste_db.get(paste_id)

    if paste is None:
        return None, "not found"

    if paste.get("expires_at"):
        if datetime.utcnow() > datetime.fromisoformat(paste["expires_at"]):
            return None, "expired"

    if paste.get("password_hash"):
        if (
            not password
            or hashlib.sha256(password.encode()).hexdigest()
            != paste["password_hash"]
        ):
            return None, "wrong password"

    return paste, None