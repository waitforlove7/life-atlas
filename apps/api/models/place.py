import enum
import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class PlaceStatus(str, enum.Enum):
    visited = "visited"
    wishlist = "wishlist"
    lived = "lived"
    worked = "worked"
    studied = "studied"


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    location = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    status: Mapped[PlaceStatus] = mapped_column(Enum(PlaceStatus, name="place_status"), default=PlaceStatus.visited)
    visit_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_image: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    city = relationship("City", back_populates="places")
    albums = relationship("Album", back_populates="place", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="place_tags", back_populates="places")
