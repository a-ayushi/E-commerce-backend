"""Add owner_id to products

Revision ID: 80f463a5ae41
Revises: 
Create Date: 2025-06-12 07:35:18.881057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80f463a5ae41'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('products', sa.Column('owner_id', sa.Integer(), nullable=False, server_default='1'))
    op.create_foreign_key(None, 'products', 'users', ['owner_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'owner_id')
   