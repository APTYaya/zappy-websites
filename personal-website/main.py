from fastapi import FastAPI
from contextlib import asynccontextmanager 

from src.backend.models.database import init_db
from src.backend.routers import blog, games, music, projects, videos

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield 


app = FastAPI(lifespan=lifespan)

# Routers 
app.include_router(blog.router)
app.include_router(games.router)
app.include_router(music.router)
app.include_router(projects.router)
app.include_router(videos.router)                   