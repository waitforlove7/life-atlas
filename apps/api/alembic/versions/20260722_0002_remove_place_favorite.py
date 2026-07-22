"""Remove the unused place favorite flag.

Revision ID: 20260722_0002
Revises: 20260722_0001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260722_0002"
down_revision: Union[str, None] = "20260722_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("places", "favorite")


def downgrade() -> None:
    op.add_column(
        "places", sa.Column("favorite", sa.Boolean(), nullable=False, server_default=sa.false())
    )
    op.alter_column("places", "favorite", server_default=None)
