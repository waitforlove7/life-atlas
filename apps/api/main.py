from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from core.database import engine, Base
from routers import places


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Enable PostGIS extension (required for geometry columns)
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS postgis'))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Life Atlas API", lifespan=lifespan)

app.include_router(places.router)


@app.get("/")
def root():
    return {"message": "Life Atlas API running"}
