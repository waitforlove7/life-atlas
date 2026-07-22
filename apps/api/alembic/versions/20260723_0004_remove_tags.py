"""Remove the unused tag feature.

Revision ID: 20260723_0004
Revises: 20260722_0003
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260723_0004"
down_revision: Union[str, None] = "20260723_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("place_tags")
    op.drop_table("tags")


def downgrade() -> None:
    raise RuntimeError("The removed tag data cannot be restored automatically.")
