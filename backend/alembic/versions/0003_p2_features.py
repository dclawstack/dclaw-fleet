"""P2 features — EV, accidents, parts inventory, telematics, dashcam

Revision ID: 0003_p2_features
Revises: 0002_p1_features
Create Date: 2026-05-21
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0003_p2_features"
down_revision = "0002_p1_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "charging_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("station_id", sa.String(128), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("energy_kwh", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("soc_start", sa.Float(), nullable=True),
        sa.Column("soc_end", sa.Float(), nullable=True),
    )
    op.create_index("ix_charging_sessions_vehicle_id", "charging_sessions", ["vehicle_id"])

    op.create_table(
        "accident_reports",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", UUID(as_uuid=True), sa.ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity_score", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("photos_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("claim_status", sa.String(32), nullable=False, server_default="open"),
        sa.Column("claim_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("predicted_claim_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accident_reports_vehicle_id", "accident_reports", ["vehicle_id"])

    op.create_table(
        "parts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("sku", sa.String(64), nullable=False, unique=True),
        sa.Column("category", sa.String(32), nullable=False),
        sa.Column("vendor", sa.String(128), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_threshold", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("unit_cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "telematics_devices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vendor", sa.String(64), nullable=False),
        sa.Column("device_id", sa.String(128), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_telematics_devices_vehicle_id", "telematics_devices", ["vehicle_id"])

    op.create_table(
        "dashcam_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vehicle_id", UUID(as_uuid=True), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", UUID(as_uuid=True), sa.ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(32), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("video_url", sa.String(512), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dashcam_events_vehicle_id", "dashcam_events", ["vehicle_id"])
    op.create_index("ix_dashcam_events_recorded_at", "dashcam_events", ["recorded_at"])


def downgrade() -> None:
    op.drop_index("ix_dashcam_events_recorded_at", table_name="dashcam_events")
    op.drop_index("ix_dashcam_events_vehicle_id", table_name="dashcam_events")
    op.drop_table("dashcam_events")

    op.drop_index("ix_telematics_devices_vehicle_id", table_name="telematics_devices")
    op.drop_table("telematics_devices")

    op.drop_table("parts")

    op.drop_index("ix_accident_reports_vehicle_id", table_name="accident_reports")
    op.drop_table("accident_reports")

    op.drop_index("ix_charging_sessions_vehicle_id", table_name="charging_sessions")
    op.drop_table("charging_sessions")
