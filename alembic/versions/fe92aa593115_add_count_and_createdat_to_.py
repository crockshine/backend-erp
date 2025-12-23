"""add_count_and_createdat_to_ordertosupplier

Revision ID: fe92aa593115
Revises: 755278361bee
Create Date: 2025-12-22 22:59:08.987908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe92aa593115'
down_revision: Union[str, Sequence[str], None] = '755278361bee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем поле count (сначала nullable, потом заполним)
    op.add_column('OrderToSupplier', sa.Column('count', sa.Integer(), nullable=True))

    # Заполняем значением по умолчанию для существующих записей
    op.execute('UPDATE "OrderToSupplier" SET count = 1 WHERE count IS NULL')

    # Делаем поле NOT NULL
    op.alter_column('OrderToSupplier', 'count', nullable=False)

    # Добавляем поле createdAt
    op.add_column('OrderToSupplier', sa.Column('createdAt', sa.DateTime(), nullable=True))

    # Заполняем текущей датой для существующих записей
    op.execute('UPDATE "OrderToSupplier" SET "createdAt" = NOW() WHERE "createdAt" IS NULL')

    # Делаем поле NOT NULL
    op.alter_column('OrderToSupplier', 'createdAt', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('OrderToSupplier', 'createdAt')
    op.drop_column('OrderToSupplier', 'count')
