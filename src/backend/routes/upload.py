import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from src.backend.utils.files import UPLOAD_DIR as FILE_UPLOAD_DIR
from src.backend.utils.videos import UPLOAD_DIR as VIDEO_UPLOAD_DIR
from src.backend.utils.database import get_connection
from src.backend.utils.templates import templates
from datetime import datetime
import secrets

router = APIRouter()

TEMP_DIR = "uploads/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_number: int = Form(...),
    file_type: str = Form(...),
    chunk: UploadFile = File(...),
):
    chunk_dir = os.path.join(TEMP_DIR, upload_id)
    os.makedirs(chunk_dir, exist_ok=True)

    chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_number:04d}")
    contents = await chunk.read()
    with open(chunk_path, "wb") as f:
        f.write(contents)

    return JSONResponse({"status": "ok", "chunk": chunk_number})

@router.get("/upload/status/{upload_id}")
def upload_status(upload_id: str):
    chunk_dir = os.path.join(TEMP_DIR, upload_id)
    if not os.path.exists(chunk_dir):
        return JSONResponse({"received_chunks": []})

    chunks = os.listdir(chunk_dir)
    received = sorted([int(f.split("_")[1]) for f in chunks if f.startswith("chunk_")])

    return JSONResponse({"received_chunks": received})

@router.post("/upload/complete")
async def upload_complete(
    request: Request,
    upload_id: str = Form(...),
    filename: str = Form(...),
    file_type: str = Form(...),
    total_chunks: int = Form(...),
    expiration_hours: int = Form(1),
    password: str = Form(None),
    burn: bool = Form(False),
):
    chunk_dir = os.path.join(TEMP_DIR, upload_id)
    received = os.listdir(chunk_dir)
    received_numbers = sorted([int(f.split("_")[1]) for f in received if f.startswith("chunk_")])
    
    if len(received_numbers) != total_chunks:
        return JSONResponse({"status": "error", "message": "missing chunks"}, status_code=400)
    
    file_id = secrets.token_urlsafe(8)
    extension = os.path.splitext(filename)[1]
    stored_name = f"{file_id}{extension}"
    
    if file_type == "video":
        final_path = os.path.join(VIDEO_UPLOAD_DIR, stored_name)
    else:
        final_path = os.path.join(FILE_UPLOAD_DIR, stored_name)
    
    with open(final_path, "wb") as final:
        for i in range(total_chunks):
            chunk_path = os.path.join(chunk_dir, f"chunk_{i:04d}")
            with open(chunk_path, "rb") as chunk:
                final.write(chunk.read())
    
    shutil.rmtree(chunk_dir)
    
    import hashlib
    from datetime import timedelta
    password_hash = None
    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
    expires_at = None
    if expiration_hours:
        expires_at = (datetime.utcnow() + timedelta(hours=expiration_hours)).isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if file_type == "video":
        cursor.execute("""
            INSERT INTO videos (id, filename, title, mimetype, size, created_at, expires_at, password_hash, burn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file_id, stored_name, filename, "video/mp4", os.path.getsize(str(final_path)), datetime.utcnow().isoformat(), expires_at, password_hash, burn))
        url = f"/v/{file_id}"
    else:
        import mimetypes
        mimetype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        cursor.execute("""
            INSERT INTO files (id, filename, original_name, mimetype, size, created_at, expires_at, password_hash, burn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file_id, stored_name, filename, mimetype, os.path.getsize(str(final_path)), datetime.utcnow().isoformat(), expires_at, password_hash, burn))
        url = f"/f/{file_id}"
    
    conn.commit()
    conn.close()
    
    return JSONResponse({"status": "ok", "url": url})