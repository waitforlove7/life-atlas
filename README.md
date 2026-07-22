# Atlas ¡ª Your Personal World Atlas

A personal world atlas that records where you've been, lived, studied, and explored.

## Project Structure

`
atlas/
©À©¤©¤ apps/
©¦   ©À©¤©¤ web/                 # Next.js + TypeScript frontend
©¦   ©¸©¤©¤ api/                 # FastAPI backend
©À©¤©¤ packages/
©¦   ©À©¤©¤ ui/                  # Shared React components
©¦   ©À©¤©¤ types/               # Shared TypeScript types
©¦   ©À©¤©¤ map/                 # MapLibre GL wrapper
©¦   ©¸©¤©¤ utils/               # Shared utilities
©À©¤©¤ database/
©¦   ©À©¤©¤ migrations/          # Database migrations
©¦   ©À©¤©¤ seed/                # Seed data
©¦   ©¸©¤©¤ schema.sql           # Core schema
©À©¤©¤ storage/
©¦   ©¸©¤©¤ covers/              # Place cover images (dev)
©À©¤©¤ docker/                  # Docker configs
©À©¤©¤ docs/                    # Documentation
©À©¤©¤ docker-compose.yml
©À©¤©¤ package.json
©¸©¤©¤ README.md
`

## Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

## Setup

### 1. Clone

`ash
git clone https://github.com/waitforlove7/life-atlas.git
cd life-atlas
`

### 2. Start PostgreSQL

`ash
docker compose up -d
`

### 3. Set up the API

`ash
cd apps/api
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
`

API ¡ú http://localhost:8000

### 4. Set up the frontend

`ash
cd apps/web
npm install
npm run dev
`

Frontend ¡ú http://localhost:3000

## Environment Variables

Copy .env.example to .env:

`ash
cp .env.example .env
`

## Tech Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Frontend | Next.js, TypeScript, TailwindCSS, shadcn/ui |
| Backend  | FastAPI, Python         |
| Database | PostgreSQL + PostGIS    |
| Storage  | MinIO (planned), local files (dev) |
| Infra    | Docker Compose          |
