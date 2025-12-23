"""remove_imageurl_from_product

Revision ID: 5d0af68c8a5a
Revises: 991cd28cd1e3
Create Date: 2025-12-21 18:00:27.694300

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d0af68c8a5a'
down_revision: Union[str, Sequence[str], None] = '991cd28cd1e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove imageUrl column from Product table
    op.drop_column('Product', 'imageUrl')


def downgrade() -> None:
    """Downgrade schema."""
    # Add imageUrl column back to Product table
    op.add_column('Product', sa.Column('imageUrl', sa.String(), nullable=True))
    # If you want to make it non-nullable again, you'd need to fill it with default values first

