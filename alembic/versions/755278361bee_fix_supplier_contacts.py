"""fix_supplier_contacts

Revision ID: 755278361bee
Revises: 5d0af68c8a5a
Create Date: 2025-12-22 22:05:46.439210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '755278361bee'
down_revision: Union[str, Sequence[str], None] = '5d0af68c8a5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем старые колонки phone и location если они существуют
    # Добавляем новую колонку contacts
    op.add_column('Supplier', sa.Column('contacts', sa.String(), nullable=True))

    # Копируем данные из phone в contacts если есть данные
    op.execute("""
        UPDATE "Supplier" 
        SET contacts = COALESCE(phone, '') 
        WHERE contacts IS NULL
    """)

    # Делаем contacts NOT NULL
    op.alter_column('Supplier', 'contacts', nullable=False)

    # Удаляем старые колонки
    op.drop_column('Supplier', 'phone')
    op.drop_column('Supplier', 'location')


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем обратно
    op.add_column('Supplier', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('Supplier', sa.Column('location', sa.String(), nullable=True))

    # Копируем обратно
    op.execute("""
        UPDATE "Supplier" 
        SET phone = contacts 
        WHERE phone IS NULL
    """)

    op.drop_column('Supplier', 'contacts')
