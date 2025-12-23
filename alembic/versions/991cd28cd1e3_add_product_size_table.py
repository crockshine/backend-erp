"""add_product_size_table

Revision ID: 991cd28cd1e3
Revises: 5d433d8724b3
Create Date: 2025-12-21 17:07:59.017446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '991cd28cd1e3'
down_revision: Union[str, Sequence[str], None] = '5d433d8724b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу ProductSize
    op.create_table(
        'ProductSize',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('value')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('ProductSize')

