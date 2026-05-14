import secrets
from datetime import datetime
from src.backend.utils.database import get_connection

def generate_token(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth")
    count = cursor.fetchone()[0]
    if count >= 50:
        conn.close()
        return None, "max users reached"
    token = f"tok_{secrets.token_urlsafe(16)}"
    cursor.execute("""
        INSERT INTO auth (token, name, created_at)
        VALUES (?, ?, ?)
    """, (token, name, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return token, None

def validate_token(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def revoke_token(token):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth WHERE token = ?", (token,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return None, "token not found"
    cursor.execute("DELETE FROM auth WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return True, None

def list_tokens():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM auth")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"token": row["token"], "name": row["name"], "created_at": row["created_at"]}
        for row in rows
    ]
