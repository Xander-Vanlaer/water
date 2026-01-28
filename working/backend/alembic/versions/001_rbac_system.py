"""Add RBAC tables and fields

Revision ID: 001_rbac_system
Revises: 
Create Date: 2026-01-28 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_rbac_system'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create regions table
    op.create_table('regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regions_id'), 'regions', ['id'], unique=False)
    op.create_unique_constraint('uq_regions_name', 'regions', ['name'])
    op.create_unique_constraint('uq_regions_code', 'regions', ['code'])

    # Create hospitals table
    op.create_table('hospitals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hospitals_id'), 'hospitals', ['id'], unique=False)
    op.create_unique_constraint('uq_hospitals_name', 'hospitals', ['name'])
    op.create_unique_constraint('uq_hospitals_code', 'hospitals', ['code'])

    # Create sensor_data table
    op.create_table('sensor_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('sensor_id', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
        sa.Column('air_quality', sa.Float(), nullable=True),
        sa.Column('data_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sensor_data_id'), 'sensor_data', ['id'], unique=False)
    op.create_index(op.f('ix_sensor_data_sensor_id'), 'sensor_data', ['sensor_id'], unique=False)
    op.create_index(op.f('ix_sensor_data_timestamp'), 'sensor_data', ['timestamp'], unique=False)

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('hospital_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_keys_id'), 'api_keys', ['id'], unique=False)
    op.create_index(op.f('ix_api_keys_key'), 'api_keys', ['key'], unique=False)
    op.create_unique_constraint('uq_api_keys_key', 'api_keys', ['key'])

    # Add RBAC columns to users table
    op.add_column('users', sa.Column('role', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('region_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('hospital_id', sa.Integer(), nullable=True))
    
    op.create_foreign_key('fk_users_region_id', 'users', 'regions', ['region_id'], ['id'])
    op.create_foreign_key('fk_users_hospital_id', 'users', 'hospitals', ['hospital_id'], ['id'])


def downgrade() -> None:
    # Remove foreign keys from users table
    op.drop_constraint('fk_users_hospital_id', 'users', type_='foreignkey')
    op.drop_constraint('fk_users_region_id', 'users', type_='foreignkey')
    
    # Remove RBAC columns from users table
    op.drop_column('users', 'hospital_id')
    op.drop_column('users', 'region_id')
    op.drop_column('users', 'role')

    # Drop api_keys table
    op.drop_index(op.f('ix_api_keys_key'), table_name='api_keys')
    op.drop_index(op.f('ix_api_keys_id'), table_name='api_keys')
    op.drop_table('api_keys')

    # Drop sensor_data table
    op.drop_index(op.f('ix_sensor_data_timestamp'), table_name='sensor_data')
    op.drop_index(op.f('ix_sensor_data_sensor_id'), table_name='sensor_data')
    op.drop_index(op.f('ix_sensor_data_id'), table_name='sensor_data')
    op.drop_table('sensor_data')

    # Drop hospitals table
    op.drop_index(op.f('ix_hospitals_id'), table_name='hospitals')
    op.drop_table('hospitals')

    # Drop regions table
    op.drop_index(op.f('ix_regions_id'), table_name='regions')
    op.drop_table('regions')
