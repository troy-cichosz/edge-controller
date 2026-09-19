from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TemporalContext(BaseModel):
    """Canonical temporal provenance associated with an acquisition point.

    This model is a common domain contract. It does not make edge-controller
    the time broker or the authoritative source of timing data. Evidence
    services obtain the underlying context directly from their local
    edge-time instance and may preserve it with the evidence they create.
    """

    context_id: UUID

    capture_utc: datetime
    capture_monotonic_ns: int

    device_id: str

    selected_source: str
    source_observation: dict[str, Any] = Field(default_factory=dict)
    uncertainty_ms: float
    freshness: str
    freshness_age_ms: float
    synchronization_state: str

    authority_id: str | None = None
    authority_source: str | None = None

    consistency_state: str
    consistency_offset_ms: float | None = None
    consistency_uncertainty_ms: float | None = None
    consistency_threshold_ms: float | None = None

    holdover_state: str

    attestation_sequence: int
    attestation_record_hash: str
    attestation_signature: str | None = None


class EvidenceTime(BaseModel):
    """Canonical time description for an evidence artifact.

    A point-in-time artifact uses one temporal context. An interval may use
    separate start and end contexts when the producing service acquires them.
    The temporal context is provenance for the acquisition timing; it is not
    a claim that every physical sample or sensor exposure occurred exactly at
    the recorded UTC instant.
    """

    capture_position: Literal["instant", "interval"]

    start_utc: datetime
    end_utc: datetime | None = None

    start_monotonic_ns: int
    end_monotonic_ns: int | None = None

    start_context_id: UUID
    end_context_id: UUID | None = None

    uncertainty_ms: float


class EvidenceSource(BaseModel):
    """Identity of the service and source that produced an evidence artifact."""

    device_id: str
    service_id: str
    source_id: str
    component_id: str | None = None


class EvidenceIntegrity(BaseModel):
    """Integrity state for an evidence artifact or referenced artifact.

    A verification result describes what the platform verified at a particular
    point in time. It does not itself establish legal authenticity or chain of
    custody.
    """

    algorithm: str
    content_hash: str
    verification_status: Literal["unverified", "verified", "failed"] = "unverified"
    verification_method: str | None = None
    verified_utc: datetime | None = None
    verifier: str | None = None


class EvidenceManifestEntry(BaseModel):
    """Integrity metadata for one artifact represented by a manifest."""

    evidence_id: UUID
    reference: str | None = None
    size_bytes: int | None = None
    content_hash: str
    media_type: str | None = None
    role: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceManifest(BaseModel):
    """A signed/hashable inventory describing one or more evidence artifacts.

    A manifest is descriptive integrity/provenance metadata. The manifest does
    not transfer evidence ownership to edge-controller or make the controller
    the authoritative evidence store.
    """

    manifest_id: UUID
    format_version: str
    algorithm: str
    created_utc: datetime
    entries: list[EvidenceManifestEntry] = Field(default_factory=list)
    manifest_hash: str
    attestation_id: UUID | None = None
    signature: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CustodyRecord(BaseModel):
    """Auditable platform handling/provenance record for an evidence artifact.

    This records platform custody/provenance events such as acquisition,
    verification, transfer, export, or derivation. It is not by itself a legal
    conclusion that a jurisdiction's chain-of-custody requirements are met.
    """

    custody_id: UUID
    evidence_id: UUID
    action: str
    actor_type: Literal["device", "service", "operator", "system"]
    actor_id: str
    recorded_utc: datetime
    temporal_context_id: UUID | None = None
    previous_record_hash: str | None = None
    record_hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class DerivativeRelation(BaseModel):
    """Provenance relationship between source and derived evidence."""

    relation_id: UUID
    source_evidence_id: UUID
    derivative_evidence_id: UUID
    operation: str
    processor: EvidenceSource
    created_utc: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """Common description of an authoritative or derived evidence artifact.

    This is a domain contract, not a controller persistence model. Evidence
    remains owned by the producing evidence service; the controller may later
    store or index metadata about it without becoming the evidence authority.
    """

    evidence_id: UUID
    vehicle_id: UUID | None = None
    event_id: UUID | None = None

    source: EvidenceSource
    evidence_type: str

    time: EvidenceTime

    location_context: dict[str, Any] | None = None
    configuration_id: UUID | None = None
    calibration_id: UUID | None = None

    content_hash: str
    manifest_id: UUID | None = None
    attestation_id: UUID | None = None
    signature: str | None = None

    derivative_of: UUID | None = None
    parent_evidence_id: UUID | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class Observation(BaseModel):
    """Measured, detected, or reported information associated with a source."""

    observation_id: UUID
    vehicle_id: UUID | None = None
    event_id: UUID | None = None

    source: EvidenceSource
    observation_type: str
    time: EvidenceTime

    value: Any
    unit: str | None = None
    confidence: float | None = None

    evidence_ids: list[UUID] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    """Bounded context on the canonical timeline connecting related records."""

    event_id: UUID
    vehicle_id: UUID | None = None

    event_type: str
    time: EvidenceTime

    trigger_source: EvidenceSource | None = None

    evidence_ids: list[UUID] = Field(default_factory=list)
    observation_ids: list[UUID] = Field(default_factory=list)
    related_event_ids: list[UUID] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class TimelineEntry(BaseModel):
    """A canonical timeline reference to an evidence, observation, or event."""

    entry_id: UUID
    vehicle_id: UUID | None = None

    entry_type: Literal["evidence", "observation", "event"]
    record_id: UUID
    time: EvidenceTime

    metadata: dict[str, Any] = Field(default_factory=dict)