# Life Atlas

Life Atlas is a personal travel and life map for recording places you have visited, lived in, worked in, studied in, or plan to visit.

## Features

- Country, province/state, and place map navigation
- Place statuses: `visited`, `wishlist`, `lived`, `worked`, and `studied`
- Place details, descriptions, cover images, and visit records
- Monthly visit timeline and statistics dashboard
- PostgreSQL + PostGIS geospatial storage

## Quick Start

Requirements: Docker Desktop.

    docker compose up -d --build

Open the frontend at http://localhost:3000, the API at http://localhost:8000, and API docs at http://localhost:8000/docs.

Useful commands:

    docker compose ps
    docker compose logs -f api
    docker compose down

## Local Development

Start the database:

    docker compose up -d db

Set up and start the backend:

    cd apps/api
    python -m venv venv
    .\\venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
    alembic upgrade head
    python -m uvicorn main:app --reload --port 8000

Start the frontend in a second terminal:

    cd apps/web
    npm install
    npm run dev

If PowerShell blocks `npm.ps1`, use `npm.cmd run dev`.

## API

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | API health check |
| GET | `/places` | Get places |
| GET | `/stats/summary` | Summary statistics |
| GET | `/stats/countries` | Country statistics |
| GET | `/stats/provinces` | Province/state statistics |
| GET | `/stats/status-breakdown` | Place status distribution |
| GET | `/stats/timeline` | Monthly visits and cumulative visits |

The timeline uses `visits.visit_date`, not place creation time. Multiple visits to the same place are counted as separate visit records.

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+asyncpg://atlas:atlas@localhost:5432/lifeatlas` | Database connection URL |
| `BACKEND_PORT` | `8000` | Backend port |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Frontend API URL |

## Troubleshooting

For `API unavailable: http://localhost:8000/...`, start the backend and verify http://localhost:8000/.

For `/stats/timeline` returning 500, run migrations and restart the backend:

    cd apps/api
    alembic upgrade head

Boundary files are stored in `apps/web/public/data`. Regenerate them with `python scripts/fetch_boundaries.py`. See [docs/map-boundaries.md](docs/map-boundaries.md).

## Project Structure

    Life-Atlas/
    ├─ apps/api/       # FastAPI backend
    ├─ apps/web/       # Next.js frontend
    ├─ database/       # Database resources
    ├─ docs/           # Documentation
    ├─ docker/         # Dockerfiles
    ├─ scripts/        # Utility scripts
    └─ storage/        # Local storage
