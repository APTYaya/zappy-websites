from typing import Optional

from fastapi import APIRouter, Request, Form

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from src.backend.utils.auth import validate_token, list_tokens
from src.backend.utils.templates import templates

router= APIRouter()

@router.get("/")
def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@router.post("/auth")
def authenticate(request: Request, token: str = Form(...)):
    username = validate_token(token)
    if not username:
        return templates.TemplateResponse("welcome.html", {
            "request": request,
            "username": None,
            "error": "Invalid auth token",
        })
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 365,
    )
    return response





















        