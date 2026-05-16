import secrets
import hashlib

from datetime import datetime, timedelta
from src.backend.utils.database import get_connection


def save_paste(content, language, expiration_hours=1, password=None, burn=False):
    paste_id = secrets.token_urlsafe(8)

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
        INSERT INTO pastes(id, content, language, created_at, expires_at, password_hash, burn)
        VALUES(?,?,?,?,?,?,?)
    """,(paste_id, content, language, datetime.utcnow().isoformat(), expires_at, password_hash, burn))
    conn.commit()
    conn.close()
    return paste_id


def load_paste(paste_id, password=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pastes WHERE id = ?",(paste_id,))
    paste = cursor.fetchone()
    conn.close

    if paste is None:
        return None, "not found"

    if paste["expires_at"]:
        if datetime.utcnow() > datetime.fromisoformat(paste["expires_at"]):
            return None, "expired"

    if paste["password_hash"]:
        if (
            not password
            or hashlib.sha256(password.encode()).hexdigest()
            != paste["password_hash"]
        ):
            return None, "wrong password"

    return paste, None