# Map boundary data

Atlas uses Natural Earth for its country and first-level administrative
boundaries. Natural Earth data is in the public domain.

Generate the browser assets from the repository root:

```powershell
python scripts/fetch_boundaries.py
```

The command writes one compact GeoJSON file per country to
`apps/web/public/data/admin1`, plus `countries.geojson` and an ADM1 index. The
application never downloads boundary data at runtime.

Natural Earth models map-scale political geography. It is appropriate for this
personal atlas, but it is not a legal or cadastral boundary source. Some small
territories do not have a separate ADM1 layer; they remain usable as a country
and can store a synthetic first-level region when a Place is created.

## Database upgrade note

The first Alembic revision detects the pre-Alembic City-based development
schema and upgrades it in place. Existing Places are reassigned to their
existing Province, and historical City rows are retained without deleting data.
Legacy Provinces receive stable internal `LEGACY-*` codes. New Places should be
created from the map so they use the matching Natural Earth province code.
