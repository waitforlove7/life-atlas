# Atlas 鈥?Your Personal World Atlas

A personal world atlas that records where you've been, lived, studied, and explored.

## Quick Start (Docker)

```bash
# 1. Ensure boundary data exists
python scripts/fetch_boundaries.py

# 2. Start everything
docker compose up -d

# 3. Open http://localhost:3000
```

That is it. The compose file starts PostgreSQL + PostGIS, the FastAPI backend,
and the Next.js frontend in one command.

### Modifying after build

The Docker images are immutable 鈥?edit source files, then rebuild and restart:

```bash
docker compose build   # rebuild changed layers (cache speeds this up)
docker compose up -d   # restart with new images
```

Your data (places, photos, tags) lives in the database and the `covers` volume,
so it survives rebuilds.

### Development (without Docker for the apps)

```bash
# Start only the database
docker compose up -d db

# API
cd apps/api
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000

# Frontend
cd apps/web
npm install
npm run dev
```

API 鈫?http://localhost:8000
Frontend 鈫?http://localhost:3000

## Project Structure

```text
atlas/
鈹溾攢鈹€ apps/
鈹?  鈹溾攢鈹€ web/                 # Next.js + TypeScript frontend
鈹?  鈹斺攢鈹€ api/                 # FastAPI backend
鈹溾攢鈹€ packages/
鈹?  鈹溾攢鈹€ ui/                  # Shared React components
鈹?  鈹溾攢鈹€ types/               # Shared TypeScript types
鈹?  鈹溾攢鈹€ map/                 # MapLibre GL wrapper
鈹?  鈹斺攢鈹€ utils/               # Shared utilities
鈹溾攢鈹€ docker/
鈹?  鈹溾攢鈹€ Dockerfile.api       # FastAPI production image
鈹?  鈹斺攢鈹€ Dockerfile.web       # Next.js production image
鈹溾攢鈹€ database/
鈹?  鈹溾攢鈹€ migrations/          # Database migrations
鈹?  鈹溾攢鈹€ seed/                # Seed data
鈹?  鈹斺攢鈹€ schema.sql           # Core schema
鈹溾攢鈹€ storage/
鈹?  鈹斺攢鈹€ covers/              # Place cover images (dev)
鈹溾攢鈹€ scripts/                 # Utility scripts (boundary fetch, etc.)
鈹溾攢鈹€ docker-compose.yml
鈹溾攢鈹€ package.json
鈹斺攢鈹€ README.md
```

## Tech Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Frontend | Next.js, TypeScript, TailwindCSS, shadcn/ui |
| Backend  | FastAPI, Python         |
| Database | PostgreSQL + PostGIS    |
| Storage  | MinIO (planned), local files (dev) |
| Infra    | Docker Compose          |

## Map hierarchy

Atlas intentionally uses three map levels:

```text
Country 鈫?Province / first-level region 鈫?Place
```

Countries and provinces are gray until they contain a non-wishlist Place. The
visited color is calculated from Places instead of stored as a separate flag,
so deleting the last Place immediately turns its regions gray again.

Global country and first-level boundary assets are generated from public-domain
Natural Earth data. See `docs/map-boundaries.md`.

## Environment Variables

Copy `.env.example` to `.env` for local development. Docker Compose sets
these automatically.

| Variable             | Default                                                 |
| -------------------- | ------------------------------------------------------- |
| DATABASE_URL         | postgresql+asyncpg://atlas:atlas@localhost:5432/lifeatlas |
| NEXT_PUBLIC_API_URL  | http://localhost:8000                                   |
