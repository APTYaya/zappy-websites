import os

from typing import Optional

from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File,
    BackgroundTasks,
)

from fastapi.responses import (
    FileResponse,
    StreamingResponse,
)

from fastapi.templating import Jinja2Templates

from src.backend.utils.videos import (
    save_video,
    load_video,
    video_streamer,
)

from src.backend.utils.cleanup import delete_video

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/videos")
def video_uploader(request: Request):
    return templates.TemplateResponse(
        "videos.html",
        {"request": request},
    )


@router.post("/videos")
async def create_upload_video(
    request: Request,
    file: UploadFile = File(...),
    expiration_hours: int = Form(1),
    password: Optional[str] = Form(None),
    burn: bool = Form(False),
):
    video_id = await save_video(
        file,
        expiration_hours=expiration_hours,
        password=password,
        burn=burn,
    )

    video_url = f"http://{request.headers['host']}/v/{video_id}"

    return templates.TemplateResponse(
        "videos.html",
        {
            "request": request,
            "video_url": video_url,
        },
    )


@router.get("/v/{video_id}")
def video_page(
    request: Request,
    video_id: str,
    password: Optional[str] = None,
):
    video, error = load_video(video_id, password=password)

    if error:
        if error == "expired":
            delete_video(video_id)

        return templates.TemplateResponse(
            "videos.html",
            {
                "request": request,
                "error": error,
                "video_id": video_id,
            },
        )

    return templates.TemplateResponse(
        "videos.html",
        {
            "request": request,
            "video": video,
            "video_id": video_id,
        },
    )


@router.get("/v/{video_id}/download")
def download_video(
    video_id: str,
    background_tasks: BackgroundTasks,
    password: Optional[str] = None,
):
    video, error = load_video(video_id, password=password)

    if error:
        if error == "expired":
            delete_video(video_id)

        return {"error": error}

    if video.get("burn"):
        background_tasks.add_task(delete_video, video_id)

    return FileResponse(
        path=f"uploads/videos/{video['stored_video_name']}",
        filename=video["original_name"],
        media_type=video["content_type"],
        background=background_tasks,
    )


@router.get("/v/{video_id}/stream")
async def stream_video(
    video_id: str,
    request: Request,
    password: Optional[str] = None,
):
    video, error = load_video(video_id, password=password)

    if error:
        if error == "expired":
            delete_video(video_id)

        return {"error": error}

    file_path = f"uploads/videos/{video['stored_video_name']}"

    file_size = os.path.getsize(file_path)

    range_header = request.headers.get("range")

    if range_header:
        start, end = range_header.replace("bytes=", "").split("-")

        start = int(start)
        end = int(end) if end else file_size - 1

        status_code = 206

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": video["content_type"],
        }

    else:
        start = 0
        end = file_size - 1

        status_code = 200

        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": video["content_type"],
        }

    return StreamingResponse(
        video_streamer(file_path, start, end + 1),
        status_code=status_code,
        headers=headers,
    )