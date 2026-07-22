from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    status: str = Field(default="visited", pattern=r"^(visited|wishlist|lived|worked|studied)$")
    visits: list[date] = []
    description: str | None = None
    cover_image: str | None = None
    # Location hierarchy — create or look up by name
    country_name: str = Field(..., min_length=1, max_length=100)
    country_iso: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    province_name: str = Field(..., min_length=1, max_length=200)
    province_code: str = Field(..., min_length=1, max_length=32)


class PlaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=300)
    longitude: float | None = Field(None, ge=-180, le=180)
    latitude: float | None = Field(None, ge=-90, le=90)
    status: str | None = Field(None, pattern=r"^(visited|wishlist|lived|worked|studied)$")
    visits: list[date] = []
    description: str | None = None
    cover_image: str | None = Field(None, max_length=500)


class AlbumResponse(BaseModel):
    id: UUID
    image_url: str
    caption: str | None
    taken_at: date | None

    model_config = {"from_attributes": True}


class VisitResponse(BaseModel):
    id: UUID
    visit_date: date

    model_config = {"from_attributes": True}


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    longitude: float
    latitude: float
    status: str
    visits: list["VisitResponse"] = []
    description: str | None
    cover_image: str | None
    country: str
    country_iso: str
    province: str
    province_code: str
    created_at: datetime
    albums: list[AlbumResponse] = []

    model_config = {"from_attributes": True}


class PlaceSummary(BaseModel):
    id: UUID
    name: str
    longitude: float
    latitude: float
    status: str
    country: str
    country_iso: str
    province: str
    province_code: str

    model_config = {"from_attributes": True}
