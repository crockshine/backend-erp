"""remove_imageurl_from_productcategory

Revision ID: 5d433d8724b3
Revises: 6052261efe2e
Create Date: 2025-12-20 22:57:22.179608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d433d8724b3'
down_revision: Union[str, Sequence[str], None] = '6052261efe2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем колонку imageUrl из таблицы ProductCategory
    op.drop_column('ProductCategory', 'imageUrl')


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем колонку imageUrl (если нужен откат)
    op.add_column('ProductCategory', sa.Column('imageUrl', sa.String(), nullable=True))

