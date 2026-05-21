"""P1 features — driving events, HOS, DVIR, permits, expenses, route sync columns

Revision ID: 0002_p1_features
Revises: 0001_init
Create Date: 2026-05-21
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0002_p1_features"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "driving_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("driver_id", UUID(as_uuid=True), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_driving_events_driver_id", "driving_events", ["driver_id"])
    op.create_index("ix_driving_events_vehicle_id", "driving_events", ["vehicle_id"])
    op.create_index("ix_driving_events_recorded_at", "driving_events", ["recorded_at"])

    op.create_table(
        "hos_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("driver_id", UUID(as_uuid=True), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("duty_status", sa.String(16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("miles", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_hos_logs_driver_id", "hos_logs", ["driver_id"])

    op.create_table(
        "dvir_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("driver_id", UUID(as_uuid=True), sa.ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("inspection_type", sa.String(16), nullable=False),
        sa.Column("defects_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dvir_reports_driver_id", "dvir_reports", ["driver_id"])
    op.create_index("ix_dvir_reports_vehicle_id", "dvir_reports", ["vehicle_id"])

    op.create_table(
        "permits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String(16), nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("permit_type", sa.String(64), nullable=False),
        sa.Column("issuer", sa.String(128), nullable=True),
        sa.Column("permit_number", sa.String(128), nullable=False),
        sa.Column("issued_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_permits_entity_id", "permits", ["entity_id"])
    op.create_index("ix_permits_expiry_date", "permits", ["expiry_date"])

    op.create_table(
        "expenses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("driver_id", UUID(as_uuid=True), sa.ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=True),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("approval_status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("approved_by", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_expenses_category", "expenses", ["category"])

    op.add_column("routes", sa.Column("external_id", sa.String(128), nullable=True))
    op.add_column("routes", sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_routes_external_id", "routes", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_routes_external_id", table_name="routes")
    op.drop_column("routes", "synced_at")
    op.drop_column("routes", "external_id")

    op.drop_index("ix_expenses_category", table_name="expenses")
    op.drop_table("expenses")

    op.drop_index("ix_permits_expiry_date", table_name="permits")
    op.drop_index("ix_permits_entity_id", table_name="permits")
    op.drop_table("permits")

    op.drop_index("ix_dvir_reports_vehicle_id", table_name="dvir_reports")
    op.drop_index("ix_dvir_reports_driver_id", table_name="dvir_reports")
    op.drop_table("dvir_reports")

    op.drop_index("ix_hos_logs_driver_id", table_name="hos_logs")
    op.drop_table("hos_logs")

    op.drop_index("ix_driving_events_recorded_at", table_name="driving_events")
    op.drop_index("ix_driving_events_vehicle_id", table_name="driving_events")
    op.drop_index("ix_driving_events_driver_id", table_name="driving_events")
    op.drop_table("driving_events")
