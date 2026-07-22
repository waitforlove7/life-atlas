from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import get_db
from models.place import Place
from models.tag import Tag
from schemas.place import TagCreate, TagResponse

router = APIRouter(prefix="/places/{place_id}/tags", tags=["tags"])


async def _place_with_tags(place_id: UUID, db: AsyncSession) -> Place:
    place = (await db.execute(select(Place).where(Place.id == place_id).options(selectinload(Place.tags)))).scalar_one_or_none()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.post("", response_model=TagResponse, status_code=201)
async def add_tag(place_id: UUID, payload: TagCreate, db: AsyncSession = Depends(get_db)) -> TagResponse:
    place = await _place_with_tags(place_id, db)
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Tag name is required")
    tag = (await db.execute(select(Tag).where(func.lower(Tag.name) == name.lower()))).scalar_one_or_none()
    if tag is None:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
    if tag not in place.tags:
        place.tags.append(tag)
    await db.commit()
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
async def remove_tag(place_id: UUID, tag_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    place = await _place_with_tags(place_id, db)
    tag = next((item for item in place.tags if item.id == tag_id), None)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag is not linked to this place")
    place.tags.remove(tag)
    await db.commit()
