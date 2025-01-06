from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ff16ef8b8246'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('avatar', sa.Column('name', sa.String(), nullable=True))
    op.add_column('avatar', sa.Column('type', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('avatar', 'type')
    op.drop_column('avatar', 'name')
