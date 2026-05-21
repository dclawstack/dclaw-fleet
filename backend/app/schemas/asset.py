import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetBase(BaseModel):
    name: str
    asset_type: str
    serial_number: str | None = None
    status: str = "available"
    location: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: str | None = None
    asset_type: str | None = None
    serial_number: str | None = None
    status: str | None = None
    location: str | None = None


class AssetRead(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
