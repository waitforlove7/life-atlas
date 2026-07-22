from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from models.city import City
from models.country import Country
from models.place import Place
from models.province import Province
from schemas.place import PlaceCreate, PlaceResponse, PlaceSummary

router = APIRouter(prefix="/places", tags=["places"])


def _point_to_lonlat(point):
    """Convert a WKB geometry to (longitude, latitude) tuple."""
    if point is None:
        return (0.0, 0.0)
    geom = to_shape(point)
    return (geom.x, geom.y)


def _build_response(place: Place) -> PlaceResponse:
    lon, lat = _point_to_lonlat(place.location)
    return PlaceResponse(
        id=place.id,
        name=place.name,
        longitude=lon,
        latitude=lat,
        status=place.status.value if hasattr(place.status, "value") else place.status,
        visit_date=place.visit_date,
        description=place.description,
        favorite=place.favorite,
        cover_image=place.cover_image,
        country=place.city.province.country.name,
        province=place.city.province.name,
        city=place.city.name,
        created_at=place.created_at,
    )


async def _ensure_country(db: AsyncSession, name: str, iso_code: str = "") -> Country:
    result = await db.execute(select(Country).where(Country.name == name))
    country = result.scalar_one_or_none()
    if not country:
        country = Country(name=name, iso_code=iso_code or name[:3].upper())
        db.add(country)
        await db.flush()
    return country


async def _ensure_province(db: AsyncSession, name: str, country: Country) -> Province:
    result = await db.execute(
        select(Province).where(Province.name == name, Province.country_id == country.id)
    )
    province = result.scalar_one_or_none()
    if not province:
        province = Province(name=name, country_id=country.id)
        db.add(province)
        await db.flush()
    return province


async def _ensure_city(db: AsyncSession, name: str, province: Province) -> City:
    result = await db.execute(
        select(City).where(City.name == name, City.province_id == province.id)
    )
    city = result.scalar_one_or_none()
    if not city:
        city = City(name=name, province_id=province.id)
        db.add(city)
        await db.flush()
    return city


async def _cascade_visited(db: AsyncSession, city: City) -> None:
    """Mark city, province, country as visited (bottom-up cascade)."""
    city.visited = True
    province = await db.get(Province, city.province_id)
    if province:
        province.visited = True
        country = await db.get(Country, province.country_id)
        if country:
            country.visited = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("", response_model=PlaceResponse, status_code=201)
async def create_place(payload: PlaceCreate, db: AsyncSession = Depends(get_db)) -> PlaceResponse:
    """Create a place with automatic country/province/city hierarchy."""
    # Resolve or create the location hierarchy
    country = await _ensure_country(db, payload.country_name, payload.country_iso)
    province = await _ensure_province(db, payload.province_name, country)
    city = await _ensure_city(db, payload.city_name, province)

    # Create the place
    location = from_shape(Point(payload.longitude, payload.latitude), srid=4326)
    place = Place(
        name=payload.name,
        city_id=city.id,
        location=location,
        status=payload.status,
        visit_date=payload.visit_date,
        description=payload.description,
        favorite=payload.favorite,
        cover_image=payload.cover_image,
    )
    db.add(place)

    # Cascade visited upward when status is not wishlist
    if payload.status != "wishlist":
        await _cascade_visited(db, city)

    await db.commit()

    # Eager load the full chain
    stmt = (
        select(Place)
        .where(Place.id == place.id)
        .options(
            selectinload(Place.city).selectinload(City.province).selectinload(Province.country)
        )
    )
    result = await db.execute(stmt)
    place = result.scalar_one()

    return _build_response(place)


@router.get("", response_model=list[PlaceSummary])
async def list_places(
    status: str | None = None,
    favorite: bool | None = None,
    country: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[PlaceSummary]:
    """List places with optional filters."""
    stmt = (
        select(Place)
        .options(
            selectinload(Place.city).selectinload(City.province).selectinload(Province.country)
        )
    )

    if status:
        stmt = stmt.where(Place.status == status)
    if favorite is not None:
        stmt = stmt.where(Place.favorite == favorite)
    if country:
        stmt = stmt.join(Place.city).join(City.province).join(Province.country).where(Country.name == country)

    result = await db.execute(stmt)
    places = result.scalars().all()

    return [
        PlaceSummary(
            id=p.id,
            name=p.name,
            longitude=to_shape(p.location).x,
            latitude=to_shape(p.location).y,
            status=p.status.value if hasattr(p.status, "value") else p.status,
            favorite=p.favorite,
            country=p.city.province.country.name,
            city=p.city.name,
        )
        for p in places
    ]


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(place_id: UUID, db: AsyncSession = Depends(get_db)) -> PlaceResponse:
    stmt = (
        select(Place)
        .where(Place.id == place_id)
        .options(
            selectinload(Place.city).selectinload(City.province).selectinload(Province.country)
        )
    )
    result = await db.execute(stmt)
    place = result.scalar_one_or_none()

    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    return _build_response(place)


@router.delete("/{place_id}", status_code=204)
async def delete_place(place_id: UUID, db: AsyncSession = Depends(get_db)):
    place = await db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    await db.delete(place)
    await db.commit()
