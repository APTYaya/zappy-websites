import os
import json 
import secrets
from datetime import datetime

DB_PATH = "src/backend/data/auth_db.json"



def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as file:
            return json.load(file)
    return {}

def save_db(file_db):
    with open(DB_PATH, "w") as file:
        json.dump(file_db, file, indent=2)

def generate_token(name):
    auth_db = load_db()
    if len(auth_db) >=50:
        return None, "max users reached"
    token = f"tok_{secrets.token_urlsafe(16)}"
    auth_db[token] = {
        "name": name,
        "created_at": datetime.utcnow().isoformat(),
    }
    save_db(auth_db)
    return token, None

def validate_token(token):
    auth_db = load_db()
    return token in auth_db

def revoke_token(token):
    auth_db = load_db()
    if token not in auth_db:
        return None, "token not found"
    del auth_db[token]
    save_db(auth_db)
    return True, None

def list_tokens():
    auth_db = load_db()
    return [ 
        {"token": token, "name": data["name"], "created_at": data["created_at"]}
        for token, data in auth_db.items()
    ]
