"""auth — users table + seed initial admin

Revision ID: 0004_auth_users
Revises: 0003_p2_features
Create Date: 2026-05-25
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0004_auth_users"
down_revision = "0003_p2_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Seed initial admin — credentials documented in .env.example.
    # Imported lazily so older migrations don't pay the bcrypt cost.
    from passlib.context import CryptContext

    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        sa.table(
            "users",
            sa.column("id", UUID(as_uuid=True)),
            sa.column("email", sa.String),
            sa.column("name", sa.String),
            sa.column("password_hash", sa.String),
            sa.column("role", sa.String),
            sa.column("is_active", sa.Boolean),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        [
            {
                "id": uuid.uuid4(),
                "email": "admin@dclaw.io",
                "name": "DClaw Admin",
                "password_hash": pwd.hash("admin"),
                "role": "admin",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("users")
