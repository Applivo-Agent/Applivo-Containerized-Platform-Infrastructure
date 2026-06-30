"""Outreach Platform: initial tables

Revision ID: outreach_001
Revises: h2i3j4k5l6m7
Create Date: 2026-06-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "outreach_001"
down_revision = "h2i3j4k5l6m7"
branch_labels = None
depends_on = None


def upgrade():
    # ── outreach_companies ─────────────────────────────────────────────────
    op.create_table(
        "outreach_companies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("stage", sa.String(50), nullable=True),
        sa.Column("size", sa.String(50), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("remote_policy", sa.String(50), nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="warm"),
        sa.Column("status", sa.String(30), nullable=False, server_default="watching"),
        sa.Column("research_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("researched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("match_score", sa.Float, nullable=True),
        sa.Column("tech_stack", sa.JSON, nullable=True),
        sa.Column("open_roles_count", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_companies_user_id", "outreach_companies", ["user_id"])
    op.create_index("ix_outreach_companies_status", "outreach_companies", ["status"])
    op.create_index("ix_outreach_companies_domain", "outreach_companies", ["domain"])

    # ── outreach_intelligence ──────────────────────────────────────────────
    op.create_table(
        "outreach_intelligence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("outreach_companies.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("report", sa.JSON, nullable=True),
        sa.Column("executive_summary", sa.Text, nullable=True),
        sa.Column("personalization_hooks", sa.JSON, nullable=True),
        sa.Column("tech_stack", sa.JSON, nullable=True),
        sa.Column("culture_profile", sa.JSON, nullable=True),
        sa.Column("recent_news", sa.JSON, nullable=True),
        sa.Column("outreach_recommendation", sa.JSON, nullable=True),
        sa.Column("sources", sa.JSON, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_intelligence_company_id", "outreach_intelligence", ["company_id"])

    # ── outreach_contacts ──────────────────────────────────────────────────
    op.create_table(
        "outreach_contacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("outreach_companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("email_confidence", sa.Float, nullable=True),
        sa.Column("email_validity", sa.String(20), nullable=False, server_default="unverified"),
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("role_type", sa.String(30), nullable=False, server_default="other"),
        sa.Column("relationship_strength", sa.Float, nullable=False, server_default="0"),
        sa.Column("relationship_status", sa.String(30), nullable=False, server_default="not_contacted"),
        sa.Column("last_contacted", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_replied", sa.DateTime(timezone=True), nullable=True),
        sa.Column("do_not_contact", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("source", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_contacts_user_id", "outreach_contacts", ["user_id"])
    op.create_index("ix_outreach_contacts_company_id", "outreach_contacts", ["company_id"])
    op.create_index("ix_outreach_contacts_email", "outreach_contacts", ["email"])
    op.create_index("ix_outreach_contacts_relationship_status", "outreach_contacts", ["relationship_status"])

    # ── outreach_campaigns ─────────────────────────────────────────────────
    op.create_table(
        "outreach_campaigns",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("goal", sa.String(30), nullable=False, server_default="job_search"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("sequence_config", sa.JSON, nullable=True),
        sa.Column("send_window", sa.JSON, nullable=True),
        sa.Column("daily_limit", sa.Integer, nullable=False, server_default="5"),
        sa.Column("resume_id", sa.String(36), nullable=True),
        sa.Column("ab_config", sa.JSON, nullable=True),
        sa.Column("stats", sa.JSON, nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paused_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_campaigns_user_id", "outreach_campaigns", ["user_id"])
    op.create_index("ix_outreach_campaigns_status", "outreach_campaigns", ["status"])

    # ── outreach_emails ────────────────────────────────────────────────────
    op.create_table(
        "outreach_emails",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("outreach_campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("outreach_contacts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("outreach_companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sequence_position", sa.Integer, nullable=False, server_default="1"),
        sa.Column("subject", sa.String(500), nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("subject_options", sa.JSON, nullable=True),
        sa.Column("personalization_hooks", sa.JSON, nullable=True),
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("quality_breakdown", sa.JSON, nullable=True),
        sa.Column("reply_probability", sa.Float, nullable=True),
        sa.Column("from_address", sa.String(255), nullable=True),
        sa.Column("to_address", sa.String(255), nullable=True),
        sa.Column("resume_id", sa.String(36), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_message_id", sa.String(500), nullable=True),
        sa.Column("provider_thread_id", sa.String(500), nullable=True),
        sa.Column("ab_variant", sa.String(1), nullable=True),
        sa.Column("ai_model_used", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_emails_user_id", "outreach_emails", ["user_id"])
    op.create_index("ix_outreach_emails_campaign_id", "outreach_emails", ["campaign_id"])
    op.create_index("ix_outreach_emails_contact_id", "outreach_emails", ["contact_id"])
    op.create_index("ix_outreach_emails_company_id", "outreach_emails", ["company_id"])
    op.create_index("ix_outreach_emails_status", "outreach_emails", ["status"])
    op.create_index("ix_outreach_emails_scheduled_at", "outreach_emails", ["scheduled_at"])
    op.create_index("ix_outreach_emails_thread_id", "outreach_emails", ["provider_thread_id"])

    # ── outreach_conversations ─────────────────────────────────────────────
    op.create_table(
        "outreach_conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("outreach_contacts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("outreach_companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("outreach_campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("thread_id", sa.String(500), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="awaiting_reply"),
        sa.Column("sentiment", sa.String(50), nullable=True),
        sa.Column("reply_classification", sa.String(100), nullable=True),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("next_action", sa.Text, nullable=True),
        sa.Column("next_action_due", sa.DateTime(timezone=True), nullable=True),
        sa.Column("interview_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("offer_details", sa.JSON, nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("messages", sa.JSON, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_conversations_user_id", "outreach_conversations", ["user_id"])
    op.create_index("ix_outreach_conversations_status", "outreach_conversations", ["status"])
    op.create_index("ix_outreach_conversations_contact_id", "outreach_conversations", ["contact_id"])
    op.create_index("ix_outreach_conversations_thread_id", "outreach_conversations", ["thread_id"])

    # ── outreach_email_connectors ──────────────────────────────────────────
    op.create_table(
        "outreach_email_connectors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("email_address", sa.String(255), nullable=True),
        sa.Column("access_token_enc", sa.Text, nullable=True),
        sa.Column("refresh_token_enc", sa.Text, nullable=True),
        sa.Column("token_expires", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", sa.JSON, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_history_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_outreach_connector_user"),
    )
    op.create_index("ix_outreach_email_connectors_user_id", "outreach_email_connectors", ["user_id"])

    # ── outreach_followups ─────────────────────────────────────────────────
    op.create_table(
        "outreach_followups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_id", sa.String(36), sa.ForeignKey("outreach_emails.id", ondelete="CASCADE"), nullable=True),
        sa.Column("campaign_id", sa.String(36), sa.ForeignKey("outreach_campaigns.id", ondelete="CASCADE"), nullable=True),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("outreach_contacts.id", ondelete="CASCADE"), nullable=True),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("outreach_companies.id", ondelete="CASCADE"), nullable=True),
        sa.Column("sequence_position", sa.Integer, nullable=False, server_default="2"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("skip_reason", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_outreach_followups_user_id", "outreach_followups", ["user_id"])
    op.create_index("ix_outreach_followups_scheduled_at", "outreach_followups", ["scheduled_at"])
    op.create_index("ix_outreach_followups_status", "outreach_followups", ["status"])


def downgrade():
    op.drop_table("outreach_followups")
    op.drop_table("outreach_email_connectors")
    op.drop_table("outreach_conversations")
    op.drop_table("outreach_emails")
    op.drop_table("outreach_campaigns")
    op.drop_table("outreach_contacts")
    op.drop_table("outreach_intelligence")
    op.drop_table("outreach_companies")
