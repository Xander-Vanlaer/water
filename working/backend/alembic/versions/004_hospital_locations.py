"""Add hospital location fields

Revision ID: 004_hospital_locations
Revises: 003_audit_logs
Create Date: 2026-01-29 08:55:00.000000

Migration Notes:
- Adds latitude, longitude, and map_zoom columns to hospitals table
- Latitude range: -90 to 90 (validated at application level)
- Longitude range: -180 to 180 (validated at application level)
- map_zoom default is 13 (good balance for hospital location)
- Existing hospitals will have NULL coordinates until updated via admin interface
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_hospital_locations'
down_revision = '003_audit_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add location columns to hospitals table
    op.add_column('hospitals', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('hospitals', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('hospitals', sa.Column('map_zoom', sa.Integer(), nullable=False, server_default='13'))


def downgrade() -> None:
    # Remove location columns from hospitals table
    op.drop_column('hospitals', 'map_zoom')
    op.drop_column('hospitals', 'longitude')
    op.drop_column('hospitals', 'latitude')
