from typing import Optional

from fastapi import (
    APIRouter,
    Request,
    Form,
    UploadFile,
    File,
    BackgroundTasks,
)

from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from src.backend.utils.files import save_file, load_file
from src.backend.utils.cleanup import delete_file

router = APIRouter()

templates = Jinja2Templates(directory="src/templates")


@router.get("/files")
def file_uploader(request: Request):
    return templates.TemplateResponse(
        "files.html",
        {"request": request},
    )


@router.post("/files")
async def create_upload_file(
    request: Request,
    file: UploadFile = File(...),
    expiration_hours: int = Form(1),
    password: Optional[str] = Form(None),
    burn: bool = Form(False),
):
    file_id = await save_file(
        file,
        expiration_hours=expiration_hours,
        password=password,
        burn=burn,
    )

    file_url = f"http://{request.headers['host']}/f/{file_id}"

    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "file_url": file_url,
        },
    )


@router.get("/f/{file_id}")
def file_page(
    request: Request,
    file_id: str,
    password: Optional[str] = None,
):
    file, error = load_file(file_id, password=password)

    if error:
        if error == "expired":
            delete_file(file_id)

        return templates.TemplateResponse(
            "files.html",
            {
                "request": request,
                "error": error,
                "file_id": file_id,
            },
        )

    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "file": file,
            "file_id": file_id,
        },
    )


@router.get("/f/{file_id}/download")
def download_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    password: Optional[str] = None,
):
    file, error = load_file(file_id, password=password)

    if error:
        if error == "expired":
            delete_file(file_id)

        return {"error": error}

    if file.get("burn"):
        background_tasks.add_task(delete_file, file_id)

    return FileResponse(
        path=f"uploads/files/{file['stored_file_name']}",
        filename=file["original_name"],
        media_type=file["content_type"],
        background=background_tasks,
    )