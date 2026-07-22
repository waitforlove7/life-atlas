from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=300)
    longitude: float = Field(..., ge=-180, le=180)
    latitude: float = Field(..., ge=-90, le=90)
    status: str = Field(default="visited", pattern=r"^(visited|wishlist|lived|worked|studied)$")
    visit_date: date | None = None
    description: str | None = None
    favorite: bool = False
    cover_image: str | None = None
    # Location hierarchy ¡ª create or look up by name
    country_name: str = Field(..., min_length=1, max_length=100)
    country_iso: str = Field("", max_length=3)
    province_name: str = Field(..., min_length=1, max_length=200)
    city_name: str = Field(..., min_length=1, max_length=200)


class PlaceResponse(BaseModel):
    id: UUID
    name: str
    longitude: float
    latitude: float
    status: str
    visit_date: date | None
    description: str | None
    favorite: bool
    cover_image: str | None
    country: str
    province: str
    city: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PlaceSummary(BaseModel):
    id: UUID
    name: str
    longitude: float
    latitude: float
    status: str
    favorite: bool
    country: str
    city: str

    model_config = {"from_attributes": True}
