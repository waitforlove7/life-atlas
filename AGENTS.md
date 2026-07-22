# Life Atlas Development Guide


## Project Overview

Life Atlas is a personal world atlas.

Users can record:

- visited places
- lived places
- studied places
- worked places
- favorite places


## Core Features

- World/Country/Province/City/Place hierarchy
- Interactive map
- Manual place creation
- Timeline
- Statistics
- Heat map
- Photo gallery
- Life Map


## Tech Stack

Frontend:

- Next.js
- TypeScript
- TailwindCSS
- MapLibre GL


Backend:

- FastAPI
- PostgreSQL
- PostGIS


## Development Rules

- Keep frontend and backend separated
- Use TypeScript strict mode
- Write clean reusable components
- Avoid unnecessary dependencies
- Every feature should have documentation
- Commit changes with meaningful messages


## Database Rules

Main entities:

- Country
- Province
- City
- Place
- Album
- Tag


## Product Principle

Life Atlas should feel like:

Google Maps Timeline +
Personal Journal +
Photo Album