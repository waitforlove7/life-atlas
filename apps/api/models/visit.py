import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"))
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    place = relationship("Place", back_populates="visits")
