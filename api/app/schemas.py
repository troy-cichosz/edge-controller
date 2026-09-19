from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NodeCreate(BaseModel):
    node_id: str
    hostname: str
    platform: str


class NodeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    node_id: str
    hostname: str
    platform: str
    status: str
    created_at: datetime
    updated_at: datetime


class ServiceEndpointCreate(BaseModel):
    scheme: str = "http"
    port: int
    path: str = "/"


class ServiceEndpointResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    service_id: UUID
    scheme: str
    port: int
    path: str
    created_at: datetime
    updated_at: datetime


class ServiceObservationResource(BaseModel):
    id: str
    method: str = "GET"
    path: str
    enabled: bool = True
    description: str | None = None


class ServiceCreate(BaseModel):
    service_id: str
    name: str
    version: str
    endpoint: ServiceEndpointCreate | None = None

    capabilities: dict[str, bool] = Field(
        default_factory=dict,
    )

    observation_resources: list[ServiceObservationResource] = Field(
        default_factory=list,
    )


class ServiceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    service_id: str
    node_id: UUID
    name: str
    version: str
    status: str
    capabilities: dict[str, bool] | None = None
    observation_resources: list[ServiceObservationResource] | None = None
    endpoint: ServiceEndpointResponse | None = None
    created_at: datetime
    updated_at: datetime


class ServiceCapabilitiesResponse(BaseModel):
    service_id: str
    node_id: str
    capabilities: dict[str, bool]
    updated_at: datetime


class ServiceObservationResourcesResponse(BaseModel):
    service_id: str
    node_id: str
    resources: list[ServiceObservationResource]
    updated_at: datetime


class ServiceConfigurationCreate(BaseModel):
    configuration: dict


class ServiceConfigurationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    service_id: UUID
    configuration: dict
    created_at: datetime
    updated_at: datetime


class CalibrationCreate(BaseModel):
    duration_seconds: int


class CalibrationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    node_id: UUID
    service_id: str
    status: str
    duration_seconds: int | None
    result: str | None
    error: str | None
    created_at: datetime
    updated_at: datetime


class ServiceStatusCreate(BaseModel):
    status: str
    data: dict = Field(
        default_factory=dict,
    )


class ServiceStatusResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    service_id: UUID
    status: str
    data: dict
    created_at: datetime
    updated_at: datetime