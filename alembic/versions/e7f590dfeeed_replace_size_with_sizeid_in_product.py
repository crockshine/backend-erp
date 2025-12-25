"""replace_size_with_sizeid_in_product

Revision ID: e7f590dfeeed
Revises: 0d74dde72587
Create Date: 2025-12-24 17:38:17.704686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f590dfeeed'
down_revision: Union[str, Sequence[str], None] = '0d74dde72587'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем новое поле sizeId (nullable, чтобы можно было заполнить данные)
    op.add_column('Product', sa.Column('sizeId', sa.String(), nullable=True))

    # 2. Миграция данных: создаём записи в ProductSize для каждого уникального размера из Product
    #    и связываем их через sizeId
    op.execute("""
        INSERT INTO "ProductSize" (id, value)
        SELECT gen_random_uuid()::text, unique_size
        FROM (SELECT DISTINCT size as unique_size FROM "Product") AS distinct_sizes
        WHERE unique_size NOT IN (SELECT value FROM "ProductSize")
    """)

    # 3. Обновляем sizeId в Product на основе существующего поля size
    op.execute("""
        UPDATE "Product"
        SET "sizeId" = "ProductSize".id
        FROM "ProductSize"
        WHERE "Product".size = "ProductSize".value
    """)

    # 4. Добавляем foreign key constraint
    op.create_foreign_key(
        'fk_product_size',
        'Product', 'ProductSize',
        ['sizeId'], ['id'],
        ondelete='CASCADE'
    )

    # 5. Делаем sizeId NOT NULL
    op.alter_column('Product', 'sizeId', nullable=False)

    # 6. Удаляем старое поле size
    op.drop_column('Product', 'size')

    # 7. Обновляем SizeToDiscount: добавляем sizeId и удаляем size
    op.add_column('SizeToDiscount', sa.Column('sizeId', sa.String(), nullable=True))

    # Связываем существующие скидки с ProductSize
    op.execute("""
        UPDATE "SizeToDiscount"
        SET "sizeId" = "ProductSize".id
        FROM "ProductSize"
        WHERE "SizeToDiscount".size = "ProductSize".value
    """)

    # Добавляем foreign key для SizeToDiscount
    op.create_foreign_key(
        'fk_sizetodiscount_size',
        'SizeToDiscount', 'ProductSize',
        ['sizeId'], ['id'],
        ondelete='CASCADE'
    )

    # Делаем sizeId NOT NULL и удаляем старое поле size
    op.alter_column('SizeToDiscount', 'sizeId', nullable=False)
    op.drop_column('SizeToDiscount', 'size')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Восстанавливаем поле size в SizeToDiscount
    op.add_column('SizeToDiscount', sa.Column('size', sa.Integer(), nullable=True))

    # Копируем данные обратно
    op.execute("""
        UPDATE "SizeToDiscount"
        SET size = "ProductSize".value
        FROM "ProductSize"
        WHERE "SizeToDiscount"."sizeId" = "ProductSize".id
    """)

    op.alter_column('SizeToDiscount', 'size', nullable=False)
    op.drop_constraint('fk_sizetodiscount_size', 'SizeToDiscount', type_='foreignkey')
    op.drop_column('SizeToDiscount', 'sizeId')

    # 2. Восстанавливаем поле size в Product
    op.add_column('Product', sa.Column('size', sa.Integer(), nullable=True))

    # Копируем данные обратно
    op.execute("""
        UPDATE "Product"
        SET size = "ProductSize".value
        FROM "ProductSize"
        WHERE "Product"."sizeId" = "ProductSize".id
    """)

    # 3. Удаляем новое поле sizeId
    op.alter_column('Product', 'size', nullable=False)
    op.drop_constraint('fk_product_size', 'Product', type_='foreignkey')
    op.drop_column('Product', 'sizeId')

