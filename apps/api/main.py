from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.database import engine
from routers import albums, places, stats


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
storage_dir = Path(__file__).resolve().parent / "storage"
if not storage_dir.exists():
    storage_dir = Path(__file__).resolve().parents[2] / "storage"
app.mount("/storage", StaticFiles(directory=storage_dir), name="storage")


@app.get("/")
def root():
    return {"message": "Life Atlas API running"}
