"""reference flags_overrides by flag id

Revision ID: 3c2731f5c2bc
Revises: 3d00d7a4eab6
Create Date: 2026-08-17 09:23:26.661463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c2731f5c2bc'
down_revision: Union[str, Sequence[str], None] = '3d00d7a4eab6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite can't redefine a composite primary key via ALTER TABLE (even in
    # batch mode the incremental add/drop-column diff doesn't reliably merge
    # a new column into the existing composite PK), so recreate the table
    # explicitly with the target schema instead.
    op.rename_table('flags_overrides', '_flags_overrides_old')
    op.create_table(
        'flags_overrides',
        sa.Column('flag_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ['flag_id'], ['flags.id'], name='fk_flags_overrides_flag_id_flags'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], name='fk_flags_overrides_user_id_users'
        ),
        sa.PrimaryKeyConstraint('flag_id', 'user_id'),
    )
    op.execute("""
        INSERT INTO flags_overrides (flag_id, user_id, is_active)
        SELECT f.id, o.user_id, o.is_active
        FROM _flags_overrides_old o
        JOIN flags f ON f.key = o."key"
    """)
    op.drop_table('_flags_overrides_old')


def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('flags_overrides', '_flags_overrides_old')
    op.create_table(
        'flags_overrides',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ['key'], ['flags.key'], name='fk_flags_overrides_key_flags'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'], name='fk_flags_overrides_user_id_users'
        ),
        sa.PrimaryKeyConstraint('key', 'user_id'),
    )
    op.execute("""
        INSERT INTO flags_overrides ("key", user_id, is_active)
        SELECT f.key, o.user_id, o.is_active
        FROM _flags_overrides_old o
        JOIN flags f ON f.id = o.flag_id
    """)
    op.drop_table('_flags_overrides_old')
