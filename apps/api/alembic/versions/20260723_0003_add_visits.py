"""Add visits table and migrate place.visit_date data.

Revision ID: 20260723_0003
Revises: 20260722_0002
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260723_0003"
down_revision: Union[str, None] = "20260722_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "visits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("place_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        "INSERT INTO visits (id, place_id, visit_date, created_at) "
        "SELECT gen_random_uuid(), id, visit_date, created_at "
        "FROM places WHERE visit_date IS NOT NULL"
    )
    op.drop_column("places", "visit_date")


def downgrade() -> None:
    op.add_column("places", sa.Column("visit_date", sa.Date()))
    op.execute(
        "UPDATE places SET visit_date = visits.visit_date "
        "FROM visits WHERE visits.place_id = places.id"
    )
    op.drop_table("visits")
