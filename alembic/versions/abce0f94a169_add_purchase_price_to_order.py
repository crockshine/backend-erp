"""add_purchase_price_to_order

Revision ID: abce0f94a169
Revises: fe92aa593115
Create Date: 2025-12-23 00:12:42.518614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abce0f94a169'
down_revision: Union[str, Sequence[str], None] = 'fe92aa593115'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем колонку purchasePrice со значением по умолчанию 0
    op.add_column('OrderToSupplier', sa.Column('purchasePrice', sa.Float(), nullable=False, server_default='0'))
    # Убираем server_default после добавления
    op.alter_column('OrderToSupplier', 'purchasePrice', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('OrderToSupplier', 'purchasePrice')
