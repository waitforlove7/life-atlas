from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from models.country import Country
from models.province import Province
from models.city import City
from models.place import Place

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/countries")
async def get_countries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Country).order_by(Country.name))
    return [{"iso_code": c.iso_code, "name": c.name, "visited": c.visited} for c in result.scalars().all()]


@router.get("/provinces")
async def get_provinces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Province).options(selectinload(Province.country)).order_by(Province.name)
    )
    return [{"id": str(p.id), "name": p.name, "country": p.country.name, "visited": p.visited} for p in result.scalars().all()]


@router.get("/cities")
async def get_cities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(City).options(selectinload(City.province).selectinload(Province.country)).order_by(City.name)
    )
    return [{"id": str(c.id), "name": c.name, "province": c.province.name, "country": c.province.country.name, "visited": c.visited} for c in result.scalars().all()]


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    countries = (await db.execute(select(Country))).scalars().all()
    provinces = (await db.execute(select(Province))).scalars().all()
    cities = (await db.execute(select(City))).scalars().all()
    places = (await db.execute(select(Place))).scalars().all()
    return {
        "countries_total": len(countries), "countries_visited": sum(1 for c in countries if c.visited),
        "provinces_total": len(provinces), "provinces_visited": sum(1 for p in provinces if p.visited),
        "cities_total": len(cities), "cities_visited": sum(1 for c in cities if c.visited),
        "places_total": len(places),
    }
