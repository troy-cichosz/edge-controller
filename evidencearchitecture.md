# AI Legal Edge Platform - Evidence Architecture

**Document:** `evidencearchitecture.md`  
**Purpose:** Common platform model for evidence, observations, events, timelines, temporal context, provenance, integrity, derivatives, and reconstruction  
**Status:** Active architecture  
**Version:** 0.1  
**Scope:** Platform-level conceptual architecture; implementation schemas remain service-specific until formally established

**Normative status:** Architectural rules in this document are intended to guide implementation. Field names, APIs, and database schemas shown here are conceptual until explicitly promoted to an implementation contract.

---

# 1. Purpose

This document defines the common evidence architecture used to connect independently developed evidence-producing services.

It exists so that services such as `edge-video`, `edge-audio`, `edge-gps`, future vehicle telemetry, and future sensor services can contribute information without each inventing a separate evidence model.

This document defines concepts and relationships.

It does not define every service API, database schema, capture implementation, or deployment procedure.

---

# 2. Architectural Boundary

The evidence architecture follows:

```
local edge-time
      |
      v
evidence-producing service
      |
      v
local source evidence
      |
      +-- temporal context
      +-- provenance
      +-- integrity
      +-- source identity
      |
      v
common evidence model
      |
      v
observations / events / timeline
      |
      v
verification / custody
      |
      v
derived analysis / reconstruction
```

Evidence-producing services own their physical sources and local evidence.

`edge-controller` does not become the mandatory real-time capture or timestamp path.

---

# 3. Core Objects

## 3.1 Evidence

Evidence is an original or preserved data artifact produced by an evidence-producing service.

Examples include:

- video recordings
- audio recordings
- GNSS data
- vehicle telemetry
- sensor recordings
- other source-specific artifacts

Authoritative evidence is immutable after finalization.

Evidence may have associated manifests, attestations, observations, events, and derivative relationships.

## 3.2 Observation

An observation is measured, detected, or reported information associated with a source and temporal context.

Examples:

```
GNSS position observed
vehicle speed measured
camera detection produced
audio condition observed
door switch changed state
GPS fix became invalid
time authority became unavailable
```

An observation may be derived from evidence, produced directly by a service, or represent a system condition.

An observation is not automatically equivalent to an authoritative source artifact.

Derived observations must preserve source attribution and uncertainty.

## 3.3 Event

An event is a bounded context on the canonical timeline that groups related evidence and observations.

Conceptually:

```
Event
  |
  +-- event identity
  +-- vehicle
  +-- time interval
  +-- triggering source/condition
  +-- evidence
  +-- observations
  +-- system events
```

Potential triggers include manual markers, sensor conditions, vehicle state, camera/audio conditions, GNSS conditions, system conditions, or future AI detections.

Event detection itself is an observation and must retain source and uncertainty information.

## 3.4 Timeline

The timeline is the platform representation used to correlate heterogeneous temporal sources.

A timeline must preserve, where applicable:

```
UTC time
monotonic time
time-source provenance
source observation
authority relationship
uncertainty
freshness
synchronization state
holdover state
consistency information
```

Presentation must not imply precision greater than the underlying timing evidence supports.

---

# 4. Capture Time Context

Every evidence-producing service must be able to associate captured information with temporal context supplied by local `edge-time`.

Conceptually:

```
Capture Time Context
    |
    +-- UTC timestamp
    +-- monotonic timestamp
    +-- edge-time instance
    +-- selected source
    +-- source observation
    +-- authority identity
    +-- authority source
    +-- uncertainty
    +-- freshness
    +-- synchronization state
    +-- consistency measurement
    +-- holdover state
    +-- attestation reference
```

The architecture preserves the distinction between:

```
clock time
source observation
authority relationship
measurement uncertainty
cryptographic attestation
```

The Capture Time Context is provenance associated with evidence; it is not merely a formatted timestamp string.

The service-specific contract and implementation are owned by `edge-time`.

A Capture Time Context represents the temporal state observed by `edge-time` at context acquisition. Unless a source-specific capture position is separately available, it must not be described as the exact physical instant at which a camera exposure, microphone sample, GNSS measurement, or other physical acquisition occurred.

For interval evidence, such as a video or audio recording, the evidence service may associate the context with the beginning of the acquisition operation and separately preserve any source-specific start/end or media timing information that it can establish.

---

# 5. Evidence Provenance

Evidence provenance describes how and under what conditions an artifact was produced.

Where applicable, provenance should identify:

```
vehicle
device
service
source
component
capture time
time context
time source
authority
uncertainty
location context
configuration
calibration
integrity information
attestation
parent/derivative relationships
```

The exact fields may differ by evidence type.

A hash alone is not sufficient provenance.

Provenance must remain associated with the evidence rather than being reconstructed later from assumptions.

---

# 6. Common Evidence Object

The eventual common evidence object is expected to contain concepts such as:

```
evidence_id
vehicle_id
event_id

device_id
service_id
source_id
component_id

evidence_type

capture_start
capture_end

capture_timestamp_utc
capture_monotonic
time_context_id
capture_time_semantics

location_context
configuration_id
calibration_id

content_hash
manifest_id
attestation_id
signature

derivative_of
parent_evidence_id
```

`event_id` may be absent when evidence is captured before an event has been identified. Evidence should not require a pre-existing event merely to be preserved.

`capture_timestamp_utc` and `capture_monotonic` in this conceptual object refer to the associated temporal context unless a more precise source-specific capture position is available. `capture_time_semantics` identifies that distinction rather than allowing a generic timestamp field to imply unsupported physical-capture precision.

This is conceptual and is not yet a final database schema.

The final schema should be designed and reviewed before broad implementation.

## 6.1 Minimum Evidence Envelope Contract - Round 1

The first common implementation contract is limited to the concepts already demonstrated by the evidence-producing services. It standardizes the evidence envelope without standardizing modality-specific capture data.

Conceptually:

```
EvidenceEnvelope
+-- evidence_id
+-- service
+-- service_version
+-- node_id
+-- source
|   +-- source_id             # optional initially
+-- capture
|   +-- start
|   +-- end                   # optional
|   +-- monotonic_start_ns    # optional
|   +-- time_semantics
+-- time_context              # optional
+-- artifacts[]
|   +-- artifact_id
|   +-- role                  # authoritative | derived
|   +-- filename/path
|   +-- media_type
|   +-- size
|   +-- sha256
+-- configuration             # optional/reference
+-- derivation                # optional
+-- service_metadata
```

### Required common semantics

- `evidence_id` identifies the evidence envelope. A service may retain an existing service-specific capture identifier in `service_metadata`.
- `service`, `service_version`, and `node_id` identify the producer and hosting node.
- `source.source_id` is optional until a service can provide a stable source identity. Existing source-specific identity must not be replaced or fabricated merely to satisfy the envelope.
- `capture` describes the service's established capture boundary or interval. It must not imply physical acquisition precision that the source does not establish.
- `capture.time_semantics` is required whenever a capture time is represented. It identifies what the time represents, such as a service-start reference, capture-boundary context acquisition, source timestamp, or another explicitly established position.
- `time_context` contains the local `edge-time` Capture Time Context when available. Its presence does not imply exact physical exposure or sample timing unless the producing source separately establishes that position.
- `artifacts[]` identifies the preserved outputs and their integrity. Every authoritative source artifact must be explicitly marked `authoritative`; derived artifacts must be marked `derived` and retain their relationship to the authoritative source.
- `configuration` and `derivation` are optional references and must not require a new central configuration or evidence database.
- `service_metadata` preserves producer-specific fields that are outside the common envelope.

### Ownership and implementation boundary

The envelope is a common interoperability contract, not a shared implementation owner.

The producing evidence service remains responsible for:

- source-specific acquisition;
- hardware interaction;
- capture lifecycle;
- source-specific timing information;
- artifact creation and finalization;
- source-specific metadata;
- modality-specific integrity and processing behavior.

The common envelope must not cause `edge-controller` to mediate capture, timestamp acquisition, evidence creation, or artifact storage.

The common contract standardizes shared meaning and relationships; it does not standardize camera, audio, GNSS, telemetry, or other source-specific implementation details.

### Round 1 timing rule

For interval evidence, `capture.start` and `capture.end` may represent service-established boundaries rather than exact physical acquisition positions.

A temporal context acquired near a capture boundary remains a Capture Time Context association. It must not be promoted to an exact physical exposure, sample, frame, or measurement time unless the producing source provides that timing position.

This distinction is mandatory for the initial video and audio envelope implementations.

### Round 1 implementation rule

The common envelope is implemented independently by each evidence-producing service and associated with its existing service-specific evidence metadata.

Round 1 does not introduce:

- a shared Python/package dependency;
- a shared evidence database;
- controller-mediated capture;
- controller-mediated time acquisition;
- replacement of existing authoritative artifacts;
- migration of service-specific ownership into `edge-controller`.

The envelope may be represented as a manifest or sidecar alongside existing service-specific metadata, provided the authoritative source artifact remains unchanged.

---

# 7. Manifest

A manifest is a structured record connecting an evidence artifact to relevant integrity, provenance, temporal, identity, configuration, calibration, and relationship information.

A manifest may reference:

```
evidence identity
content hash
capture time context
source identity
device/service identity
configuration
calibration
attestation
derivative/parent relationships
related observations/events
```

The manifest must not become a substitute for preserving the underlying evidence.

---

# 8. Integrity and Attestation

## Integrity

Integrity mechanisms allow the system to determine whether preserved information has changed.

A content hash is one integrity mechanism.

## Attestation

An attestation is a cryptographically verifiable statement about a relevant state or record.

Attestation may provide additional assurance about identity, state, or provenance.

Neither integrity hashes nor attestations eliminate the need for contextual provenance.

Detailed cryptographic mechanisms are maintained in `wishlist.md` until promoted into a formal implementation requirement.

---

# 9. Derivatives and Derived Information

Processing must preserve the distinction between authoritative source evidence and derived information.

Examples of derived information include:

```
transcoding
transcription
OCR
computer vision
AI analysis
synchronization
overlays
reports
presentation files
inferred locations
classifications
measurements derived from source data
```

A derivative must retain its relationship to its source.

Derived observations must preserve applicable:

```
source identity
source evidence reference
processing method
model or tool identity
processing time/context
uncertainty
```

Derived results must not be represented as unquestionable source facts.

---

# 10. Evidence Immutability

Evidence has a lifecycle distinct from later analysis:

```text
capture
   |
finalize
   |
authoritative immutable source
   |
verify / copy / analyze
   |
derivatives and observations
```

Capture may produce an artifact that is not yet finalized. Finalization is the point after which the authoritative source artifact is treated as immutable.

Once authoritative source evidence is finalized:

- later configuration changes must not rewrite it;
- later calibration changes must not rewrite it;
- later time-policy changes must not rewrite it;
- synchronization must not rewrite it;
- AI processing must not rewrite it;
- overlays and presentation must not rewrite it.

Any resulting artifact is a derivative.

---

# 11. Central Copies

The architecture permits central reference or backup copies.

Conceptually:

```
LOCAL AUTHORITATIVE COPY
        +
CENTRAL REFERENCE/BACKUP COPY
```

The local copy remains authoritative unless the evidence model explicitly establishes another authority relationship.

A copy should preserve, where applicable:

```
original evidence identity
original content hash
source identity
transfer metadata
destination identity
transfer time
verification result
```

A central copy must not silently become the authoritative original.

Central copies may support presentation, correlation, backup, indexing, or AI processing.

---

# 12. Custody

Custody represents the auditable lifecycle of evidence handling.

It may eventually include:

```
collection
copy
transfer
storage
verification
analysis
derivative creation
export
```

Custody records themselves require integrity and provenance.

Detailed custody capabilities remain in `wishlist.md` until promoted into active implementation.

---

# 13. External Trusted Timestamping

External timestamp anchoring may provide an additional provenance layer when connectivity is available.

Conceptually:

```
local evidence root
       |
       v
trusted timestamp service
       |
       v
timestamp token
```

The platform must remain functional without external connectivity.

External timestamping does not replace local evidence preservation or local temporal provenance.

---

# 14. Reconstruction

Reconstruction is downstream from evidence preservation.

Conceptually:

```
source evidence
      |
      v
temporal context
      |
      v
correlation
      |
      v
event/time selection
      |
      v
reconstruction
      |
      v
presentation
```

A reconstruction may correlate:

```
video
audio
GNSS
vehicle telemetry
sensor observations
system events
transcripts
AI-derived observations
```

Reconstruction output is a derived presentation or analytical product unless a specific underlying source artifact is itself preserved as authoritative evidence.

---

# 15. Technical Evidence Boundary

The evidence architecture is intended to provide:

```
technical integrity
provenance
repeatability
traceability
verifiability
uncertainty preservation
```

It does not determine:

```
legal admissibility
evidentiary weight
legal conclusions
```

Those determinations remain outside the technical evidence model.

---

# 16. Architectural Rules

The evidence architecture must remain consistent with `projectrules.md`, particularly:

- original evidence immutability;
- provenance accompanying evidence;
- separation of derived data;
- auditability;
- temporal uncertainty;
- central-copy authority boundaries;
- technical evidence boundaries;
- uncertainty in derived results.

---

# 17. Implementation Status

This document establishes the common evidence architecture and the Round 1 minimum evidence envelope contract.

The Round 1 contract was derived from an implementation audit of the current evidence-producing services. The next implementation work is to add the envelope independently to those services while preserving their existing authoritative artifacts and service-specific metadata.

Current development status is maintained in `sprintstatus.md`.

Significant milestone and decision history is maintained in `projectstatus.md`.

Service-specific implementation belongs in the corresponding service repository documentation.
