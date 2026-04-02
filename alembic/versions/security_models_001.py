"""Add security models: CredentialVault, UserConsent, AuditLog

Revision ID: security_models_001
Revises: 6df4ff846734
Create Date: 2024-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'security_models_001'
down_revision: Union[str, None] = '6df4ff846734'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # CredentialVault Table
    # ============================================
    op.create_table(
        'credential_vaults',
        sa.Column('id', sa.String(length=36), primary_key=True, default=lambda: str(__import__('uuid').uuid4())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False, index=True),
        sa.Column('credential_type', sa.String(length=50), nullable=False, index=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('encrypted_data', sa.Text(), nullable=False),
        sa.Column('consent_given', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('consent_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('consent_purpose', sa.String(length=500), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scope', sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_credential_vaults_id'), 'credential_vaults', ['id'], unique=False)

    # ============================================
    # CredentialUseLog Table
    # ============================================
    op.create_table(
        'credential_use_logs',
        sa.Column('id', sa.String(length=36), primary_key=True, default=lambda: str(__import__('uuid').uuid4())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('credential_id', sa.String(length=36), nullable=False, index=True),
        sa.Column('user_id', sa.String(length=36), nullable=False, index=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['credential_id'], ['credential_vaults.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_credential_use_logs_id'), 'credential_use_logs', ['id'], unique=False)

    # ============================================
    # UserConsent Table
    # ============================================
    op.create_table(
        'user_consents',
        sa.Column('id', sa.String(length=36), primary_key=True, default=lambda: str(__import__('uuid').uuid4())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False, index=True),
        sa.Column('consent_type', sa.String(length=100), nullable=False, index=True),
        sa.Column('scope', sa.String(length=500), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked', sa.DateTime(timezone=True), nullable=True),
        sa.Column('policy_version', sa.String(length=50), nullable=True),
        sa.Column('purpose', sa.String(length=500), nullable=False),
        sa.Column('data_categories', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index(op.f('ix_user_consents_id'), 'user_consents', ['id'], unique=False)
    op.create_index(op.f('ix_user_consents_user_id'), 'user_consents', ['user_id'], unique=False)

    # ============================================
    # ConsentVersion Table
    # ============================================
    op.create_table(
        'consent_versions',
        sa.Column('id', sa.String(length=36), primary_key=True, default=lambda: str(__import__('uuid').uuid4())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False, unique=True),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index(op.f('ix_consent_versions_id'), 'consent_versions', ['id'], unique=False)

    # ============================================
    # AuditLog Table
    # ============================================
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True, default=lambda: str(__import__('uuid').uuid4())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('action', sa.String(length=100), nullable=False, index=True),
        sa.Column('resource_type', sa.String(length=100), nullable=True, index=True),
        sa.Column('resource_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True, index=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index(op.f('ix_consent_versions_id'), table_name='consent_versions')
    op.drop_table('consent_versions')

    op.drop_index(op.f('ix_user_consents_user_id'), table_name='user_consents')
    op.drop_index(op.f('ix_user_consents_id'), table_name='user_consents')
    op.drop_table('user_consents')

    op.drop_index(op.f('ix_credential_use_logs_id'), table_name='credential_use_logs')
    op.drop_table('credential_use_logs')

    op.drop_index(op.f('ix_credential_vaults_id'), table_name='credential_vaults')
    op.drop_table('credential_vaults')
