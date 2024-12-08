from alembic import op
import sqlalchemy as sa

revision = '000000_initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'channel_settings',
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('system', sa.String(), nullable=True),
        sa.Column('tools', sa.JSON(), nullable=True),
        sa.Column('thread_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('channel_id')
    )

def downgrade() -> None:
    op.drop_table('channel_settings') 