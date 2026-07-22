"""Create or upgrade to the country, province, and place hierarchy.

Revision ID: 20260722_0001
"""

from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import context, op
from sqlalchemy.dialects import postgresql

revision: str = "20260722_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _legacy_schema_exists() -> bool:
    if context.is_offline_mode():
        return False
    return "countries" in sa.inspect(op.get_bind()).get_table_names()


def _upgrade_legacy_schema() -> None:
    """Upgrade the pre-Alembic City-based development schema without deleting Places."""
    op.execute("DROP INDEX IF EXISTS idx_countries_visited")
    op.execute("DROP INDEX IF EXISTS idx_provinces_visited")
    op.execute("DROP INDEX IF EXISTS idx_places_city")

    op.add_column("provinces", sa.Column("code", sa.String(32), nullable=True))
    op.execute(
        "UPDATE provinces SET code = 'LEGACY-' || left(replace(id::text, '-', ''), 24) "
        "WHERE code IS NULL"
    )
    op.alter_column("provinces", "code", nullable=False)
    op.create_unique_constraint("uq_provinces_country_code", "provinces", ["country_id", "code"])

    op.add_column("places", sa.Column("province_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute(
        "UPDATE places AS place SET province_id = city.province_id "
        "FROM cities AS city WHERE place.city_id = city.id"
    )
    op.alter_column("places", "province_id", nullable=False)
    op.create_foreign_key(
        "fk_places_province", "places", "provinces", ["province_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("places_city_id_fkey", "places", type_="foreignkey")
    op.drop_column("places", "city_id")
    op.create_index("idx_places_province", "places", ["province_id"])

    op.drop_column("countries", "visited")
    op.drop_column("provinces", "visited")


def _create_schema() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    place_status = postgresql.ENUM(
        "visited", "wishlist", "lived", "worked", "studied", name="place_status", create_type=False
    )
    place_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "countries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("iso_code", sa.String(3), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "provinces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("countries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("country_id", "code"),
    )
    op.create_table(
        "places",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("province_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("provinces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("location", geoalchemy2.Geometry("POINT", srid=4326, spatial_index=False), nullable=False),
        sa.Column("status", place_status, nullable=False),
        sa.Column("visit_date", sa.Date()),
        sa.Column("description", sa.Text()),
        sa.Column("favorite", sa.Boolean(), nullable=False),
        sa.Column("cover_image", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_places_location", "places", ["location"], postgresql_using="gist")
    op.create_index("idx_places_province", "places", ["province_id"])
    op.create_index("idx_places_status", "places", ["status"])
    op.create_table(
        "albums",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("place_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("places.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("caption", sa.Text()),
        sa.Column("taken_at", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "place_tags",
        sa.Column("place_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("places.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )


def upgrade() -> None:
    if _legacy_schema_exists():
        _upgrade_legacy_schema()
        return
    _create_schema()


def downgrade() -> None:
    raise NotImplementedError("Downgrading the legacy data-preserving baseline is not supported.")
