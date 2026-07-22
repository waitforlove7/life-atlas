"""Download and normalize Natural Earth country and first-level boundaries.

Usage: python scripts/fetch_boundaries.py [--tolerance 0.01]
Outputs browser-ready files under apps/web/public/data.
Natural Earth data is in the public domain.
"""

import argparse
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

COUNTRIES_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
    "ne_10m_admin_0_countries.geojson"
)
ADMIN1_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
    "ne_10m_admin_1_states_provinces.geojson"
)
DATA_DIR = Path("apps/web/public/data")


def download_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "Life-Atlas/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def simplify_geometry(geometry: dict, tolerance: float) -> dict:
    if tolerance <= 0:
        return geometry
    try:
        from shapely.geometry import mapping, shape
    except ImportError:
        return geometry
    return mapping(shape(geometry).simplify(tolerance, preserve_topology=True))


def normalize_countries(source: dict, tolerance: float) -> dict:
    features = []
    for feature in source.get("features", []):
        props = feature.get("properties", {})
        iso_code = props.get("ISO_A3")
        if not iso_code or iso_code == "-99":
            continue
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "iso_code": iso_code,
                    "name": props.get("NAME_EN") or props.get("NAME") or iso_code,
                },
                "geometry": simplify_geometry(feature["geometry"], tolerance),
            }
        )
    return {"type": "FeatureCollection", "features": features}


def normalize_admin1(source: dict, tolerance: float) -> dict[str, list[dict]]:
    countries: dict[str, list[dict]] = defaultdict(list)
    for feature in source.get("features", []):
        props = feature.get("properties", {})
        country_iso = props.get("adm0_a3") or props.get("ADM0_A3")
        if not country_iso or country_iso == "-99":
            continue
        code = props.get("iso_3166_2") or props.get("ISO_3166_2")
        if not code or code == "-99":
            code = f"NE-{props.get('ne_id') or props.get('NE_ID')}"
        countries[country_iso].append(
            {
                "type": "Feature",
                "properties": {
                    "code": str(code),
                    "name": props.get("name_en") or props.get("name") or str(code),
                    "country_iso": country_iso,
                },
                "geometry": simplify_geometry(feature["geometry"], tolerance),
            }
        )
    return countries


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch global ADM0/ADM1 boundaries")
    parser.add_argument("--tolerance", type=float, default=0.01)
    args = parser.parse_args()

    countries = normalize_countries(download_json(COUNTRIES_URL), args.tolerance)
    admin1 = normalize_admin1(download_json(ADMIN1_URL), args.tolerance)
    write_json(DATA_DIR / "countries.geojson", countries)

    index = []
    for iso_code, features in sorted(admin1.items()):
        write_json(
            DATA_DIR / "admin1" / f"{iso_code}.geojson",
            {"type": "FeatureCollection", "features": features},
        )
        index.append({"iso_code": iso_code, "province_count": len(features)})
    write_json(DATA_DIR / "admin1" / "index.json", index)
    print(f"Wrote {len(countries['features'])} countries and {len(index)} ADM1 files")


if __name__ == "__main__":
    main()
