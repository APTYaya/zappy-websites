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
    authenticated = validate_token(token) if token else False
    return templates.TemplateResponse("welcome.html", {
        "request": request,
        "authenticated": authenticated,
    })

@router.post("/auth")
def authenticate(request: Request, token: str = Form(...)):
    is_valid = validate_token(token)
    if not is_valid:
        return templates.TemplateResponse("welcome.html", {
            "request": request,
            "authenticated": False,
            "error": "Invalid auth token",
        })
    response = templates.TemplateResponse("welcome.html", {
        "request": request,
        "authenticated": True,
    })
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        max_age= 60 * 60 * 24 * 30,
    )
    return response





















        