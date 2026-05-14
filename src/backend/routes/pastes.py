from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

from src.backend.utils.pastes import save_paste, load_paste
from src.backend.utils.cleanup import delete_paste
from src.backend.utils.templates import templates

router = APIRouter()




@router.get("/paste")
def paste_editor(request: Request):
    return templates.TemplateResponse(
        "paste.html",
        {
            "request": request,
            "mode": "create",
        },
    )


@router.post("/paste")
def create_paste(
    request: Request,
    content: str = Form(...),
    language: str = Form("plain"),
    expiration_hours: int = Form(1),
    password: Optional[str] = Form(None),
    burn: bool = Form(False),
):
    paste_id = save_paste(
        content,
        language,
        expiration_hours=expiration_hours,
        password=password,
        burn=burn,
    )

    paste_url = f"http://{request.headers['host']}/p/{paste_id}"

    return templates.TemplateResponse(
        "paste.html",
        {
            "request": request,
            "mode": "create",
            "paste_url": paste_url,
        },
    )


@router.get("/p/{paste_id}")
def view_paste(
    request: Request,
    paste_id: str,
    password: Optional[str] = None,
):
    paste, error = load_paste(paste_id, password=password)

    if error:
        if error == "expired":
            delete_paste(paste_id)

        return templates.TemplateResponse(
            "paste.html",
            {
                "request": request,
                "mode": "locked" if error == "wrong password" else "error",
                "error": error,
                "paste_id": paste_id,
            },
        )

    if paste["burn"]:
        delete_paste(paste_id)

    return templates.TemplateResponse(
        "paste.html",
        {
            "request": request,
            "mode": "view",
            "paste": paste,
            "paste_id": paste_id,
        },
    )


@router.get("/p/{paste_id}/raw")
def raw_paste(
    paste_id: str,
    password: Optional[str] = None,
):
    paste, error = load_paste(paste_id, password=password)

    if error:
        if error == "expired":
            delete_paste(paste_id)

        return {"error": error}

    content = paste["content"]

    if paste["burn"]:
        delete_paste(paste_id)

    return content