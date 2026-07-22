from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import engine, Base
from routers import places


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev convenience; use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Life Atlas API", lifespan=lifespan)

app.include_router(places.router)


@app.get("/")
def root():
    return {"message": "Life Atlas API running"}
