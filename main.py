from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from src.backend.routes import pastes, files, videos, auth
from src.backend.utils.auth import validate_token
from src.backend.utils.database import init_db

app = FastAPI()
init_db()

app.mount("/static", StaticFiles(directory="src/frontend"), name="static")
templates = Jinja2Templates(directory="src/templates")

PROTECTED = [
    "/paste",
    "/files",
    "/videos",
]

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if any(path.startswith(p) for p in PROTECTED):
        token = request.cookies.get("auth_token")
        print(f"Path: {path}, Token: {token}, Valid: {validate_token(token) if token else False}")
        if not token or not validate_token(token):
            return RedirectResponse(url="/")
    return await call_next(request)

app.include_router(auth.router)
app.include_router(pastes.router)
app.include_router(files.router)
app.include_router(videos.router)