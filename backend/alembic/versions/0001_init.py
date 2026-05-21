"""initial schema — vehicles, drivers, assets, geofences, locations, maintenance, fuel, routes, ai_chat

Revision ID: 0001_init
Revises:
Create Date: 2026-05-21
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "drivers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("license_number", sa.String(64), nullable=False, unique=True),
        sa.Column("license_expiry", sa.Date(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("safety_score", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("vin", sa.String(32), nullable=False, unique=True),
        sa.Column("license_plate", sa.String(32), nullable=False),
        sa.Column("make", sa.String(64), nullable=False),
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("fuel_type", sa.String(32), nullable=False, server_default="gasoline"),
        sa.Column("odometer_miles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engine_hours", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "driver_id",
            UUID(as_uuid=True),
            sa.ForeignKey("drivers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("asset_type", sa.String(64), nullable=False),
        sa.Column("serial_number", sa.String(128), nullable=True, unique=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="available"),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "geofences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("fence_type", sa.String(32), nullable=False, server_default="inclusion"),
        sa.Column("center_lat", sa.Float(), nullable=False),
        sa.Column("center_lng", sa.Float(), nullable=False),
        sa.Column("radius_m", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "location_pings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "vehicle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("speed_mph", sa.Float(), nullable=False, server_default="0"),
        sa.Column("heading_deg", sa.Float(), nullable=False, server_default="0"),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_location_pings_vehicle_id", "location_pings", ["vehicle_id"])
    op.create_index("ix_location_pings_recorded_at", "location_pings", ["recorded_at"])

    op.create_table(
        "maintenance_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "vehicle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("task_type", sa.String(64), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("due_mileage", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="scheduled"),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column("cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_maintenance_tasks_vehicle_id", "maintenance_tasks", ["vehicle_id"])

    op.create_table(
        "fuel_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "vehicle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "driver_id",
            UUID(as_uuid=True),
            sa.ForeignKey("drivers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("gallons", sa.Float(), nullable=False),
        sa.Column("cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("odometer_miles", sa.Integer(), nullable=False),
        sa.Column("fuel_type", sa.String(32), nullable=False, server_default="gasoline"),
        sa.Column("filled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fuel_logs_vehicle_id", "fuel_logs", ["vehicle_id"])

    op.create_table(
        "routes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        sa.Column(
            "vehicle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("vehicles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("optimized_distance_miles", sa.Float(), nullable=True),
        sa.Column("optimized_duration_min", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "route_stops",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "route_id",
            UUID(as_uuid=True),
            sa.ForeignKey("routes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
    )
    op.create_index("ix_route_stops_route_id", "route_stops", ["route_id"])

    op.create_table(
        "ai_chat_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False, server_default="Fleet Copilot"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "ai_chat_messages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_chat_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ai_chat_messages_session_id", "ai_chat_messages", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_chat_messages_session_id", table_name="ai_chat_messages")
    op.drop_table("ai_chat_messages")
    op.drop_table("ai_chat_sessions")
    op.drop_index("ix_route_stops_route_id", table_name="route_stops")
    op.drop_table("route_stops")
    op.drop_table("routes")
    op.drop_index("ix_fuel_logs_vehicle_id", table_name="fuel_logs")
    op.drop_table("fuel_logs")
    op.drop_index("ix_maintenance_tasks_vehicle_id", table_name="maintenance_tasks")
    op.drop_table("maintenance_tasks")
    op.drop_index("ix_location_pings_recorded_at", table_name="location_pings")
    op.drop_index("ix_location_pings_vehicle_id", table_name="location_pings")
    op.drop_table("location_pings")
    op.drop_table("geofences")
    op.drop_table("assets")
    op.drop_table("vehicles")
    op.drop_table("drivers")
