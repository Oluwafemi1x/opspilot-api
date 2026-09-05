"""initial schema

Revision ID: 20260905_0001
Revises: None
"""

from alembic import op
import sqlalchemy as sa

revision = "20260905_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    role = sa.Enum("owner", "admin", "member", name="membership_role")
    status = sa.Enum(
        "open",
        "in_progress",
        "blocked",
        "completed",
        "cancelled",
        name="work_order_status",
    )
    priority = sa.Enum("low", "medium", "high", "urgent", name="work_order_priority")

    op.create_table(
        "users",
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "organizations",
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)

    op.create_table(
        "memberships",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", role, nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_user_org"),
    )
    op.create_index("ix_memberships_user_id", "memberships", ["user_id"])
    op.create_index("ix_memberships_organization_id", "memberships", ["organization_id"])

    op.create_table(
        "clients",
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(320)),
        sa.Column("phone", sa.String(50)),
        sa.Column("notes", sa.Text()),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clients_organization_id", "clients", ["organization_id"])
    op.create_index("ix_clients_name", "clients", ["name"])

    op.create_table(
        "work_orders",
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("client_id", sa.Uuid(), sa.ForeignKey("clients.id", ondelete="SET NULL")),
        sa.Column("created_by_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("assigned_to_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", status, nullable=False),
        sa.Column("priority", priority, nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True)),
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    for column in ["organization_id", "client_id", "assigned_to_id", "title", "status", "priority", "due_at"]:
        op.create_index(f"ix_work_orders_{column}", "work_orders", [column])

    op.create_table(
        "audit_logs",
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
    )
    for column in ["organization_id", "action", "created_at"]:
        op.create_index(f"ix_audit_logs_{column}", "audit_logs", [column])


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("work_orders")
    op.drop_table("clients")
    op.drop_table("memberships")
    op.drop_table("organizations")
    op.drop_table("users")
    sa.Enum(name="work_order_priority").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="work_order_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="membership_role").drop(op.get_bind(), checkfirst=True)
