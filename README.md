# Life Atlas

Your personal world atlas ¡ª track places you've visited, lived, and loved.

## Project Structure

`
Life-Atlas/
©À©¤©¤ frontend/          # Next.js + TypeScript
©¦   ©¸©¤©¤ app/
©¦       ©À©¤©¤ layout.tsx
©¦       ©À©¤©¤ page.tsx
©¦       ©¸©¤©¤ globals.css
©À©¤©¤ backend/           # FastAPI
©¦   ©À©¤©¤ main.py
©¦   ©¸©¤©¤ requirements.txt
©À©¤©¤ database/          # Database migrations and schemas (future)
©À©¤©¤ docs/              # Documentation
©À©¤©¤ docker-compose.yml
©¸©¤©¤ README.md
`

## Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose

## Setup

### 1. Clone the repository

`ash
git clone https://github.com/waitforlove7/life-atlas.git
cd life-atlas
`

### 2. Start PostgreSQL

`ash
docker compose up -d
`

### 3. Set up the backend

`ash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
`

The API will be available at http://localhost:8000.

### 4. Set up the frontend

`ash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
`

The frontend will be available at http://localhost:3000.

## Environment Variables

Copy .env.example to .env and adjust as needed:

`ash
cp .env.example .env
`

## Tech Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Frontend | Next.js, TypeScript, TailwindCSS |
| Backend  | FastAPI, Python         |
| Database | PostgreSQL + PostGIS    |
| Infra    | Docker Compose          |
