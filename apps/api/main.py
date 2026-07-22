from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.database import engine
from routers import albums, places, stats, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Life Atlas API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places.router)
app.include_router(stats.router)
app.include_router(albums.router)
app.include_router(tags.router)
app.mount("/storage", StaticFiles(directory=Path(__file__).resolve().parents[2] / "storage"), name="storage")


@app.get("/")
def root():
    return {"message": "Life Atlas API running"}
