from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.country import Country
from models.place import Place, PlaceStatus
from models.province import Province
from models.visit import Visit
from services.places import MAP_LIGHTING_STATUSES

router = APIRouter(prefix="/stats", tags=["stats"])


def _visited_place_filter():
    return Place.status.in_(MAP_LIGHTING_STATUSES)


@router.get("/countries")
async def get_countries(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(
                Country.iso_code,
                Country.name,
                (func.count(Place.id).filter(_visited_place_filter()) > 0).label("visited"),
            )
            .outerjoin(Country.provinces)
            .outerjoin(Province.places)
            .group_by(Country.id)
            .order_by(Country.name)
        )
    ).all()
    return [
        {"iso_code": iso_code, "name": name, "visited": visited}
        for iso_code, name, visited in rows
    ]


@router.get("/provinces")
async def get_provinces(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(
                Province.id,
                Province.code,
                Province.name,
                Country.iso_code,
                Country.name,
                (func.count(Place.id).filter(_visited_place_filter()) > 0).label("visited"),
            )
            .join(Province.country)
            .outerjoin(Province.places)
            .group_by(Province.id, Country.id)
            .order_by(Country.name, Province.name)
        )
    ).all()
    return [
        {
            "id": str(province_id),
            "code": code,
            "name": name,
            "country_iso": country_iso,
            "country": country,
            "visited": visited,
        }
        for province_id, code, name, country_iso, country, visited in rows
    ]


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    countries_visited = await db.scalar(
        select(func.count(distinct(Country.id)))
        .join(Country.provinces)
        .join(Province.places)
        .where(_visited_place_filter())
    )
    provinces_visited = await db.scalar(
        select(func.count(distinct(Province.id)))
        .join(Province.places)
        .where(_visited_place_filter())
    )
    places_total = await db.scalar(select(func.count(Place.id)))
    return {
        "countries_visited": countries_visited or 0,
        "provinces_visited": provinces_visited or 0,
        "places_total": places_total or 0,
    }



@router.get("/status-breakdown")
async def get_status_breakdown(db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(Place.status, func.count(Place.id))
            .group_by(Place.status)
            .order_by(Place.status)
        )
    ).all()
    breakdown = {row[0].value: row[1] for row in rows}
    total = sum(breakdown.values()) or 1
    return [
        {
            "status": status.value,
            "count": breakdown.get(status.value, 0),
            "percentage": round(breakdown.get(status.value, 0) / total * 100, 1),
        }
        for status in PlaceStatus
    ]


@router.get("/timeline")
async def get_timeline(db: AsyncSession = Depends(get_db)):
    month = func.to_char(Visit.visit_date, "YYYY-MM")
    rows = (
        await db.execute(
            select(
                month.label("month"),
                func.count(Visit.id).label("count"),
            )
            .select_from(Visit)
            .group_by(month)
            .order_by(month)
        )
    ).all()
    return [
        {
            "month": str(row[0]),
            "count": row[1],
            "cumulative": sum(r[1] for r in rows[: idx + 1]),
        }
        for idx, row in enumerate(rows)
    ]
