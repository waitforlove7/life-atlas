-- ============================================================================
-- Life Atlas Database Schema
-- PostgreSQL + PostGIS
-- Run: psql -U atlas -d lifeatlas -f database/schema.sql
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------

CREATE TYPE place_status AS ENUM (
    'visited',
    'wishlist',
    'lived',
    'worked',
    'studied'
);

-- ---------------------------------------------------------------------------
-- Countries
-- ---------------------------------------------------------------------------

CREATE TABLE countries (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(100) NOT NULL UNIQUE,
    iso_code    VARCHAR(3)   NOT NULL UNIQUE,
    visited     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_countries_visited ON countries (visited);

COMMENT ON TABLE  countries IS 'Countries visited or tracked.';
COMMENT ON COLUMN countries.iso_code IS 'ISO 3166-1 alpha-3 code, e.g. CHN, JPN, SGP.';

-- ---------------------------------------------------------------------------
-- Provinces / States
-- ---------------------------------------------------------------------------

CREATE TABLE provinces (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_id  UUID         NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
    visited     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    UNIQUE (country_id, name)
);

CREATE INDEX idx_provinces_country   ON provinces (country_id);
CREATE INDEX idx_provinces_visited   ON provinces (visited);

COMMENT ON TABLE provinces IS 'Provinces, states, or equivalent first-level divisions.';

-- ---------------------------------------------------------------------------
-- Cities
-- ---------------------------------------------------------------------------

CREATE TABLE cities (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    province_id UUID         NOT NULL REFERENCES provinces(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
    visited     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    UNIQUE (province_id, name)
);

CREATE INDEX idx_cities_province ON cities (province_id);
CREATE INDEX idx_cities_visited  ON cities (visited);

COMMENT ON TABLE cities IS 'Cities or towns within a province.';

-- ---------------------------------------------------------------------------
-- Places (core entity)
-- ---------------------------------------------------------------------------

CREATE TABLE places (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city_id     UUID          NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name        VARCHAR(300)  NOT NULL,
    location    GEOMETRY(Point, 4326) NOT NULL,
    status      place_status  NOT NULL DEFAULT 'visited',
    visit_date  DATE,
    description TEXT,
    favorite    BOOLEAN       NOT NULL DEFAULT FALSE,
    cover_image VARCHAR(500),
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_places_city     ON places (city_id);
CREATE INDEX idx_places_status   ON places (status);
CREATE INDEX idx_places_favorite ON places (favorite);
CREATE INDEX idx_places_location ON places USING GIST (location);
CREATE INDEX idx_places_visit_date ON places (visit_date);

COMMENT ON TABLE  places IS 'The core entity ¡ª every spot on the map.';
COMMENT ON COLUMN places.location   IS 'SRID 4326 (WGS 84) point ¡ª longitude, latitude.';
COMMENT ON COLUMN places.status     IS 'visited | wishlist | lived | worked | studied.';
COMMENT ON COLUMN places.cover_image IS 'Relative path to cover image under storage/covers/.';

-- ---------------------------------------------------------------------------
-- Albums (photos attached to a place)
-- ---------------------------------------------------------------------------

CREATE TABLE albums (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id    UUID          NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    image_url   VARCHAR(500)  NOT NULL,
    caption     TEXT,
    taken_at    DATE,
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_albums_place ON albums (place_id);

COMMENT ON TABLE albums IS 'Photos belonging to a place.';

-- ---------------------------------------------------------------------------
-- Tags
-- ---------------------------------------------------------------------------

CREATE TABLE tags (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name       VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE tags IS 'Free-form labels: Mountain, Museum, Cafe, Temple, Beach, etc.';

-- ---------------------------------------------------------------------------
-- Place ? Tag (many-to-many)
-- ---------------------------------------------------------------------------

CREATE TABLE place_tags (
    place_id UUID NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    tag_id   UUID NOT NULL REFERENCES tags(id)   ON DELETE CASCADE,

    PRIMARY KEY (place_id, tag_id)
);

COMMENT ON TABLE place_tags IS 'Junction table linking places to tags.';

-- ============================================================================
-- Visited Cascade Logic
-- ============================================================================
--
-- When a place is created with status = 'visited', the application should
-- automatically mark the corresponding city, province, and country as
-- visited = TRUE.  This is best handled in the API layer rather than
-- database triggers, so the business rule remains explicit and testable.
--
-- Pseudo:
--   1. INSERT a place with status = 'visited'
--   2. UPDATE cities    SET visited = TRUE WHERE id = place.city_id
--   3. UPDATE provinces SET visited = TRUE WHERE id = cities.province_id
--   4. UPDATE countries SET visited = TRUE WHERE id = provinces.country_id
-- ============================================================================
