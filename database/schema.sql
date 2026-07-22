-- Atlas schema reference. Alembic is the authoritative migration source.
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE place_status AS ENUM ('visited', 'wishlist', 'lived', 'worked', 'studied');

CREATE TABLE countries (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    iso_code VARCHAR(3) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE provinces (
    id UUID PRIMARY KEY,
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    code VARCHAR(32) NOT NULL,
    name VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE (country_id, code)
);

CREATE TABLE places (
    id UUID PRIMARY KEY,
    province_id UUID NOT NULL REFERENCES provinces(id) ON DELETE CASCADE,
    name VARCHAR(300) NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    status place_status NOT NULL DEFAULT 'visited',
    visit_date DATE,
    description TEXT,
    cover_image VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX idx_places_location ON places USING GIST (location);
CREATE INDEX idx_places_province ON places (province_id);
CREATE INDEX idx_places_status ON places (status);

-- albums, tags, and place_tags remain Place-owned supporting tables.
-- Country and province "visited" state is derived from non-wishlist Places.
