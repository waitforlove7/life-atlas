# Fetch and simplify GADM administrative boundaries.
# Usage: python scripts/fetch_gadm.py SGP [CHN JPN ...] [--all] [--tolerance 0.01]

import argparse, json, os, sys, urllib.request
from pathlib import Path

GADM_BASE = 'https://geodata.ucdavis.edu/gadm/gadm4.1/json'
OUT_DIR = Path('apps/web/public/data/gadm')

def simplify_geojson(data, tolerance=0.01):
    try:
        from shapely.geometry import shape
        from shapely import simplify
    except ImportError:
        return data
    for f in data.get('features', []):
        g = f.get('geometry')
        if g and g.get('type') in ('Polygon', 'MultiPolygon'):
            try:
                s = shape(g)
                s2 = simplify(s, tolerance, preserve_topology=True)
                f['geometry'] = json.loads(json.dumps(s2.__geo_interface__))
            except: pass
    return data

def fetch_gadm(iso, level):
    url = f'{GADM_BASE}/gadm41_{iso.upper()}_{level}.json'
    print(f'  Downloading {url} ...')
    try:
        with urllib.request.urlopen(url) as r:
            if r.status != 200: return None
            return json.loads(r.read())
    except Exception as e:
        print(f'    -> error: {e}')
        return None

def process_country(iso, tolerance=0.01):
    results = {}
    for level in range(3):
        print(f'  Level {level} ...')
        data = fetch_gadm(iso, level)
        if not data:
            if level == 0:
                print(f'  No GADM data for {iso}, skipping')
                return {}
            continue
        data = simplify_geojson(data, tolerance)
        results[str(level)] = data
        print(f'    -> {len(data.get("features", []))} features')
    return results

def main():
    parser = argparse.ArgumentParser(description='Fetch GADM boundaries')
    parser.add_argument('countries', nargs='*')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--tolerance', type=float, default=0.01)
    args = parser.parse_args()

    isos = [c.upper() for c in args.countries]

    if args.all:
        sys.path.insert(0, 'apps/api')
        from core.config import settings
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session
        from models.country import Country
        sync_url = settings.database_url.replace('+asyncpg', '+psycopg2')
        engine = create_engine(sync_url)
        with Session(engine) as session:
            rows = session.execute(select(Country.iso_code).where(Country.visited == True)).scalars().all()
            isos = [c for c in rows if c]

    if not isos:
        print('No countries to fetch.')
        return

    print(f'Processing {len(isos)} countries: {isos}')

    for iso in isos:
        print(f'')
        print(f'[{iso}]')
        iso_dir = OUT_DIR / iso
        iso_dir.mkdir(parents=True, exist_ok=True)
        results = process_country(iso, args.tolerance)
        for level, data in results.items():
            out_path = iso_dir / f'level_{level}.json'
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            print(f'  -> {out_path} ({os.path.getsize(out_path)/1024:.0f} KB)')

if __name__ == '__main__':
    main()