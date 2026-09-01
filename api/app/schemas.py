from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NodeCreate(BaseModel):
    node_id: str
    hostname: str
    platform: str | None = None


class NodeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    node_id: str
    hostname: str
    platform: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class ServiceCreate(BaseModel):
    service_id: str
    name: str
    version: str | None = None


class ServiceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    service_id: str
    node_id: UUID
    name: str
    version: str | None
    status: str
    created_at: datetime
    updated_at: datetime

class ServiceConfigurationCreate(BaseModel):
    configuration: dict


class ServiceConfigurationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    service_id: UUID
    configuration: dict
    created_at: datetime
    updated_at: datetime


class CalibrationCreate(BaseModel):
    duration_seconds: int = 10


class CalibrationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    node_id: UUID
    service_id: str
    status: str
    duration_seconds: int
    result: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime
