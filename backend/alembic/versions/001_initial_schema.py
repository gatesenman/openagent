"""Initial schema — 13 core tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-06-06
"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. organizations
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True),
        sa.Column("plan_type", sa.String(50), server_default="free"),
        sa.Column("settings", sa.JSON, server_default="{}"),
        sa.Column("locale", sa.String(10), server_default="zh-CN"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 2. users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255)),
        sa.Column("avatar_url", sa.Text),
        sa.Column("hashed_password", sa.String(255)),
        sa.Column("locale", sa.String(10), server_default="zh-CN"),
        sa.Column("preferences", sa.JSON, server_default="{}"),
        sa.Column("is_active", sa.Boolean, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 3. sessions
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("title", sa.String(500)),
        sa.Column("status", sa.String(50), server_default="created"),
        sa.Column("platform", sa.String(50), server_default="ubuntu"),
        sa.Column("model", sa.String(100), server_default="agent"),
        sa.Column("mode", sa.String(50), server_default="localhost"),
        sa.Column("playbook_id", sa.String(36)),
        sa.Column("devbox_id", sa.String(255)),
        sa.Column("parent_session_id", sa.String(36)),
        sa.Column("metadata_json", sa.JSON, server_default="{}"),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 4. worklog_entries
    op.create_table(
        "worklog_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id")),
        sa.Column("entry_type", sa.String(50)),
        sa.Column("title", sa.String(500)),
        sa.Column("content", sa.Text),
        sa.Column("tool_calls", sa.JSON),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 5. knowledge_notes
    op.create_table(
        "knowledge_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("repo_id", sa.String(36)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("contents", sa.Text),
        sa.Column("trigger_description", sa.Text),
        sa.Column("scope", sa.String(50), server_default="org"),
        sa.Column("folder", sa.String(255)),
        sa.Column("pinned", sa.Boolean, server_default="0"),
        sa.Column("author_type", sa.String(20), server_default="user"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 6. playbooks
    op.create_table(
        "playbooks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("macro", sa.String(100)),
        sa.Column("scope", sa.String(50), server_default="organization"),
        sa.Column("created_by", sa.String(36)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 7. repositories
    op.create_table(
        "repositories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("provider", sa.String(50), server_default="github"),
        sa.Column("default_branch", sa.String(100), server_default="main"),
        sa.Column("deepwiki_enabled", sa.Boolean, server_default="0"),
        sa.Column("deepwiki_effort", sa.String(10), server_default="low"),
        sa.Column("deepwiki_frequency", sa.String(20), server_default="weekly"),
        sa.Column("codemap_enabled", sa.Boolean, server_default="0"),
        sa.Column("settings", sa.JSON, server_default="{}"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 8. blueprints
    op.create_table(
        "blueprints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("repo_id", sa.String(36)),
        sa.Column("target", sa.String(10), server_default="repo"),
        sa.Column("config", sa.JSON, nullable=False),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 9. snapshots
    op.create_table(
        "snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("blueprint_id", sa.String(36)),
        sa.Column("status", sa.String(50), server_default="building"),
        sa.Column("image_path", sa.Text),
        sa.Column("size_bytes", sa.BigInteger),
        sa.Column("platform", sa.String(50), server_default="ubuntu-22.04"),
        sa.Column("built_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 10. skills
    op.create_table(
        "skills",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repo_id", sa.String(36)),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("file_path", sa.String(500)),
        sa.Column("content", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 11. automations
    op.create_table(
        "automations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("name", sa.String(255)),
        sa.Column("trigger_type", sa.String(50)),
        sa.Column("trigger_config", sa.JSON),
        sa.Column("action_config", sa.JSON),
        sa.Column("enabled", sa.Boolean, server_default="1"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 12. service_users (API Keys)
    op.create_table(
        "service_users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("name", sa.String(255)),
        sa.Column("role", sa.String(50), server_default="admin"),
        sa.Column("scope", sa.String(50), server_default="organization"),
        sa.Column("api_key_hash", sa.String(255)),
        sa.Column("expires_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # 13. secrets
    op.create_table(
        "secrets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("repo_id", sa.String(36)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("encrypted_value", sa.LargeBinary),
        sa.Column("scope", sa.String(50), server_default="org"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Additional: analytics_events
    op.create_table(
        "analytics_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("session_id", sa.String(36)),
        sa.Column("event_type", sa.String(100)),
        sa.Column("metadata_json", sa.JSON),
        sa.Column("cost_usd", sa.Numeric(10, 4)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Additional: code_embeddings
    op.create_table(
        "code_embeddings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("repo_id", sa.String(36)),
        sa.Column("file_path", sa.String(500)),
        sa.Column("chunk_text", sa.Text),
        sa.Column("chunk_start_line", sa.Integer),
        sa.Column("chunk_end_line", sa.Integer),
        sa.Column("embedding_json", sa.JSON),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Additional: audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36)),
        sa.Column("user_id", sa.String(36)),
        sa.Column("session_id", sa.String(36)),
        sa.Column("action", sa.String(100)),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", sa.String(36)),
        sa.Column("details", sa.JSON),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("hmac_signature", sa.String(128)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Additional: members
    op.create_table(
        "members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("role", sa.String(50), server_default="member"),
        sa.Column("email", sa.String(255)),
        sa.Column("display_name", sa.String(255)),
        sa.Column("teams", sa.JSON, server_default="[]"),
        sa.Column("is_active", sa.Boolean, server_default="1"),
        sa.Column("joined_at", sa.DateTime, server_default=sa.func.now()),
    )

    # Additional: schedules
    op.create_table(
        "schedules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("org_id", sa.String(36), sa.ForeignKey("organizations.id")),
        sa.Column("name", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("schedule_type", sa.String(50)),
        sa.Column("cron_expression", sa.String(100)),
        sa.Column("interval_minutes", sa.Integer),
        sa.Column("run_at", sa.DateTime),
        sa.Column("prompt", sa.Text),
        sa.Column("model", sa.String(100)),
        sa.Column("mode", sa.String(50)),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("max_runs", sa.Integer, server_default="0"),
        sa.Column("last_run_at", sa.DateTime),
        sa.Column("next_run_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "schedules", "members", "audit_logs", "code_embeddings",
        "analytics_events", "secrets", "service_users", "automations",
        "skills", "snapshots", "blueprints", "repositories", "playbooks",
        "knowledge_notes", "worklog_entries", "sessions", "users",
        "organizations",
    ]:
        op.drop_table(table)
