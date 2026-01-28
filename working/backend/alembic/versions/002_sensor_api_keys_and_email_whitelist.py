"""Add sensor-based API keys and email whitelist

Revision ID: 002_sensor_api_keys
Revises: 001_rbac_system
Create Date: 2026-01-28 13:30:00.000000

Migration Notes:
- Adds sensor_id field to api_keys (initially nullable for existing records)
- Adds is_validated field for admin approval workflow
- Creates allowed_emails table for registration whitelist
- After migration, existing API keys should be updated with sensor_ids manually
  or regenerated to ensure sensor_id is populated
- Existing user emails should be added to allowed_emails table if needed

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_sensor_api_keys'
down_revision = '001_rbac_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add sensor_id and is_validated columns to api_keys table
    # sensor_id is nullable initially to allow migration of existing records
    # New API keys will require sensor_id (enforced at application level)
    op.add_column('api_keys', sa.Column('sensor_id', sa.String(length=100), nullable=True))
    op.add_column('api_keys', sa.Column('is_validated', sa.Boolean(), nullable=False, server_default='false'))
    
    # Create index on sensor_id
    op.create_index(op.f('ix_api_keys_sensor_id'), 'api_keys', ['sensor_id'], unique=False)
    
    # Create allowed_emails table
    op.create_table('allowed_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_allowed_emails_id'), 'allowed_emails', ['id'], unique=False)
    op.create_index(op.f('ix_allowed_emails_email'), 'allowed_emails', ['email'], unique=True)
    
    # Note: After migration, you should:
    # 1. Add existing user emails to allowed_emails table
    # 2. Update existing API keys with appropriate sensor_ids or regenerate them


def downgrade() -> None:
    # Drop allowed_emails table
    op.drop_index(op.f('ix_allowed_emails_email'), table_name='allowed_emails')
    op.drop_index(op.f('ix_allowed_emails_id'), table_name='allowed_emails')
    op.drop_table('allowed_emails')
    
    # Remove columns from api_keys
    op.drop_index(op.f('ix_api_keys_sensor_id'), table_name='api_keys')
    op.drop_column('api_keys', 'is_validated')
    op.drop_column('api_keys', 'sensor_id')
