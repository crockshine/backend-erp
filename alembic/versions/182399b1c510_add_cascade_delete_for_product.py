"""add_cascade_delete_for_product

Revision ID: 182399b1c510
Revises: abce0f94a169
Create Date: 2025-12-23 08:49:31.149246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '182399b1c510'
down_revision: Union[str, Sequence[str], None] = 'abce0f94a169'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Обновляем внешние ключи для добавления ON DELETE CASCADE

    # ShopRest
    op.drop_constraint('ShopRest_productId_fkey', 'ShopRest', type_='foreignkey')
    op.create_foreign_key(
        'ShopRest_productId_fkey',
        'ShopRest', 'Product',
        ['productId'], ['id'],
        ondelete='CASCADE'
    )

    # ProductToSale
    op.drop_constraint('ProductToSale_ProductId_fkey', 'ProductToSale', type_='foreignkey')
    op.create_foreign_key(
        'ProductToSale_ProductId_fkey',
        'ProductToSale', 'Product',
        ['ProductId'], ['id'],
        ondelete='CASCADE'
    )

    # OrderToSupplier
    op.drop_constraint('OrderToSupplier_ProductId_fkey', 'OrderToSupplier', type_='foreignkey')
    op.create_foreign_key(
        'OrderToSupplier_ProductId_fkey',
        'OrderToSupplier', 'Product',
        ['ProductId'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем без CASCADE

    op.drop_constraint('ShopRest_productId_fkey', 'ShopRest', type_='foreignkey')
    op.create_foreign_key(
        'ShopRest_productId_fkey',
        'ShopRest', 'Product',
        ['productId'], ['id']
    )

    op.drop_constraint('ProductToSale_ProductId_fkey', 'ProductToSale', type_='foreignkey')
    op.create_foreign_key(
        'ProductToSale_ProductId_fkey',
        'ProductToSale', 'Product',
        ['ProductId'], ['id']
    )

    op.drop_constraint('OrderToSupplier_ProductId_fkey', 'OrderToSupplier', type_='foreignkey')
    op.create_foreign_key(
        'OrderToSupplier_ProductId_fkey',
        'OrderToSupplier', 'Product',
        ['ProductId'], ['id']
    )

