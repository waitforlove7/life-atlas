from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from models.country import Country
from models.album import Album
from models.place import Place, PlaceStatus
from models.province import Province
from models.tag import Tag
from schemas.place import AlbumResponse, PlaceCreate, PlaceResponse, PlaceSummary, PlaceUpdate, TagResponse

router = APIRouter(prefix="/places", tags=["places"])


def _status_value(status: PlaceStatus | str) -> str:
    return status.value if isinstance(status, PlaceStatus) else status


def _build_response(place: Place) -> PlaceResponse:
    point = to_shape(place.location)
    return PlaceResponse(
        id=place.id,
        name=place.name,
        longitude=point.x,
        latitude=point.y,
        status=_status_value(place.status),
        visit_date=place.visit_date,
        description=place.description,
        cover_image=place.cover_image,
        country=place.province.country.name,
        country_iso=place.province.country.iso_code,
        province=place.province.name,
        province_code=place.province.code,
        created_at=place.created_at,
        albums=[AlbumResponse.model_validate(album) for album in place.albums],
        tags=[TagResponse.model_validate(tag) for tag in place.tags],
    )


async def _ensure_country(db: AsyncSession, name: str, iso_code: str) -> Country:
    country = (
        await db.execute(select(Country).where(Country.iso_code == iso_code))
    ).scalar_one_or_none()
    if country is None:
        country = (
            await db.execute(select(Country).where(Country.name == name))
        ).scalar_one_or_none()
        if country is not None and country.iso_code != iso_code:
            iso_owner = (
                await db.execute(select(Country.id).where(Country.iso_code == iso_code))
            ).scalar_one_or_none()
            if iso_owner is None:
                country.iso_code = iso_code
    if country is None:
        country = Country(name=name, iso_code=iso_code)
        db.add(country)
        await db.flush()
    return country


async def _ensure_province(
    db: AsyncSession, name: str, code: str, country: Country
) -> Province:
    province = (
        await db.execute(
            select(Province).where(
                Province.code == code, Province.country_id == country.id
            )
        )
    ).scalar_one_or_none()
    if province is None:
        province = Province(name=name, code=code, country_id=country.id)
        db.add(province)
        await db.flush()
    return province


def _with_geography():
    return (
        selectinload(Place.province).selectinload(Province.country),
        selectinload(Place.albums),
        selectinload(Place.tags),
    )


@router.post("", response_model=PlaceResponse, status_code=201)
async def create_place(
    payload: PlaceCreate, db: AsyncSession = Depends(get_db)
) -> PlaceResponse:
    country = await _ensure_country(db, payload.country_name, payload.country_iso)
    province = await _ensure_province(
        db, payload.province_name, payload.province_code, country
    )
    place = Place(
        name=payload.name,
        province_id=province.id,
        location=from_shape(Point(payload.longitude, payload.latitude), srid=4326),
        status=payload.status,
        visit_date=payload.visit_date,
        description=payload.description,
        cover_image=payload.cover_image,
    )
    db.add(place)
    await db.commit()

    result = await db.execute(
        select(Place).where(Place.id == place.id).options(*_with_geography())
    )
    return _build_response(result.scalar_one())


@router.get("", response_model=list[PlaceSummary])
async def list_places(
    status: PlaceStatus | None = None,
    country: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[PlaceSummary]:
    stmt = select(Place).options(*_with_geography())
    if status:
        stmt = stmt.where(Place.status == status)
    if country:
        stmt = (
            stmt.join(Place.province)
            .join(Province.country)
            .where(Country.iso_code == country.upper())
        )

    places = (await db.execute(stmt.order_by(Place.visit_date.desc()))).scalars().all()
    return [
        PlaceSummary(
            id=place.id,
            name=place.name,
            longitude=to_shape(place.location).x,
            latitude=to_shape(place.location).y,
            status=_status_value(place.status),
            country=place.province.country.name,
            country_iso=place.province.country.iso_code,
            province=place.province.name,
            province_code=place.province.code,
        )
        for place in places
    ]


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(
    place_id: UUID, db: AsyncSession = Depends(get_db)
) -> PlaceResponse:
    place = (
        await db.execute(
            select(Place).where(Place.id == place_id).options(*_with_geography())
        )
    ).scalar_one_or_none()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return _build_response(place)


@router.patch("/{place_id}", response_model=PlaceResponse)
async def update_place(
    place_id: UUID, payload: PlaceUpdate, db: AsyncSession = Depends(get_db)
) -> PlaceResponse:
    place = (
        await db.execute(
            select(Place).where(Place.id == place_id).options(*_with_geography())
        )
    ).scalar_one_or_none()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")

    changes = payload.model_dump(exclude_unset=True)
    longitude = changes.pop("longitude", None)
    latitude = changes.pop("latitude", None)
    if longitude is not None or latitude is not None:
        current_point = to_shape(place.location)
        place.location = from_shape(
            Point(
                current_point.x if longitude is None else longitude,
                current_point.y if latitude is None else latitude,
            ),
            srid=4326,
        )
    for field, value in changes.items():
        setattr(place, field, value)

    await db.commit()
    await db.refresh(place)
    result = await db.execute(
        select(Place).where(Place.id == place.id).options(*_with_geography())
    )
    return _build_response(result.scalar_one())


@router.delete("/{place_id}", status_code=204)
async def delete_place(place_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    place = await db.get(Place, place_id)
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    await db.delete(place)
    await db.commit()
