from typing import Optional

from fastapi import APIRouter, Request, Form

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from src.backend.utils.auth import validate_token, list_tokens

router= APIRouter()

templates = Jinja2Templates(directory="src/templates")

@router.get("/")
def welcome(request: Request):
    token = request.cookies.get("auth_token")
    username = validate_token(token) if token else None
    return templates.TemplateResponse("welcome.html", {
        "request": request,
        "username": username,
    })

@router.post("/auth")
def authenticate(request: Request, token: str = Form(...)):
    username = validate_token(token)
    if not username:
        return templates.TemplateResponse("welcome.html", {
            "request": request,
            "username": None,
            "error": "Invalid auth token",
        })
    response = templates.TemplateResponse("welcome.html", {
        "request": request,
        "username": username,
    })
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        max_age=60 * 60 * 24 * 365,
    )
    return response





















        