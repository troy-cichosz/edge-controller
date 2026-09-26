# Architectural Rules

These rules define enduring architectural and engineering invariants for the AI Legal Edge Platform. They are not a sprint tracker, implementation status report, or service-specific operating guide.

## Rule 1 - Generic Controller

`edge-controller` remains service-agnostic.

Do not add service-specific branches when generic metadata, capabilities, observations, relationships, or configuration can represent the requirement.

## Rule 2 - Dynamic Discovery

A node may host any number of services.

The controller must discover actual node/service relationships dynamically, and the GUI must not assume that a node hosts only one particular service.

## Rule 3 - Hardware Ownership

Hardware-specific operations belong in the corresponding edge service.

```text
GNSS hardware          -> edge-gps
audio hardware         -> edge-audio
camera hardware        -> edge-video
vehicle/OBD hardware   -> future edge-vehicle
time calculation       -> edge-time
management policy      -> edge-controller
```

## Rule 4 - Container First

The controller and deployable edge services remain container-first.

Host-level access is permitted where required by hardware or platform integration, but containerization remains the default deployment model.

## Rule 5 - PostgreSQL

Durable controller management state belongs in PostgreSQL.

Do not introduce another database unless a demonstrated architectural requirement justifies it.

## Rule 6 - Host-Addressed HTTP

Cross-service HTTP uses the hosting node's hostname or IP address together with the host-exposed port.

Never use Docker container or service names as cross-host service endpoints.

## Rule 7 - Evidence Locality

Evidence is created and preserved on or near the producing device.

Normal evidence capture must not depend on `edge-controller`.

The controller is not part of the mandatory real-time evidence path.

## Rule 8 - Local Time Service

Evidence-producing services obtain timing context directly from local `edge-time`.

Correct:

```text
edge-video
    |
    +-- local edge-time
```

Incorrect:

```text
edge-video
    |
    v
edge-controller
    |
    v
edge-time
```

The controller is not a timestamp broker or real-time time engine.

## Rule 9 - Controller Policy Boundary

The controller owns management, configuration, discovery, and policy coordination.

It does not perform real-time time calculation, replace local time services, or become the authority for evidence-producing services' capture operations.

## Rule 10 - Original Evidence Immutability

Once finalized, authoritative evidence must not be silently rewritten.

Later changes to configuration, calibration, time policy, AI processing, synchronization, overlays, or presentation must not modify the original evidence artifact.

## Rule 11 - Provenance Accompanies Evidence

A hash alone is not sufficient.

Evidence provenance must, where applicable, preserve information such as:

```text
device
service
source
capture time
time source
authority
uncertainty
location
configuration
calibration
integrity
attestation
```

The exact fields may vary by evidence type, but provenance must remain associated with the evidence rather than being discarded or reconstructed from assumption later.

## Rule 12 - Derived Data Is Separate

AI analysis, transcoding, transcription, OCR, computer vision, synchronization, overlays, reports, and other processing produce derivatives or observations.

They do not replace authoritative source evidence.

Derived outputs must retain their relationship to the source evidence from which they were produced.

## Rule 13 - Auditability

Changes affecting evidence integrity or provenance must be auditable.

This includes, where applicable:

```text
configuration changes
calibration changes
time-policy changes
authority changes
evidence handling
verification actions
derivative creation
administrative actions affecting evidence metadata or retention
```

## Rule 14 - Generic Observation

The controller observes declared service resources without interpreting service-specific response semantics.

Service-specific meaning remains owned by the service that produces the response.

## Rule 15 - Observation Scope

Node-scoped observation may expose detailed service responses.

Fleet-scoped observation should remain compact, generic, and suitable for overview/status use without embedding service-specific interpretation into controller logic.

## Rule 16 - Verification Before Expansion

A feature is complete only after the applicable sequence has been satisfied:

```text
architecture agreed
    |
implemented
    |
built
    |
deployed
    |
runtime verified
    |
failure behavior understood where applicable
    |
documentation updated
```

## Rule 17 - Wishlist Preservation

The wishlist (`wishlist.md`) is intentional project-scope context.

Wishlist items are not current implementation commitments unless deliberately promoted into the roadmap, but future work must not be deleted merely because it is not currently scheduled.

The wishlist should be preserved as a source of planned or anticipated capabilities during documentation cleanup and architectural review.

## Rule 18 - Common Evidence Architecture

`evidencearchitecture.md` is the project-level home for the common evidence architecture.

It defines the conceptual cross-service model for Evidence, Observation, Event, Timeline, Capture Time Context, provenance, integrity, derivatives, central copies, custody, and reconstruction.

Service-specific implementations, APIs, storage layouts, and database schemas remain in their owning service repositories until explicitly promoted to a common platform contract.

Changes to this common model must remain consistent with the enduring invariants in this file and must not silently redefine service ownership.

## Rule 19 - Temporal Uncertainty

Temporal correlation and presentation must preserve the uncertainty, freshness, provenance, and synchronization limitations of the underlying timing evidence.

The platform must not imply precision unsupported by the source timing information.

## Rule 20 - Central Copy Authority

Central copies, replicas, indexes, and processing stores are derived or reference copies unless the evidence model explicitly establishes another authority relationship.

Copies must preserve source identity, the original content hash, transfer metadata, destination identity where applicable, transfer time, and verification results.

A central copy must not silently become the authoritative original.

## Rule 21 - Technical Evidence Boundary

The platform seeks technical integrity, provenance, repeatability, and verifiability for preserved information.

It does not determine legal admissibility, evidentiary weight, or legal conclusions.

## Rule 22 - Uncertainty in Derived Results

Measurements, detections, classifications, inferred locations, and AI-derived observations must preserve source attribution and uncertainty.

Derived conclusions must not be represented as unquestionable source facts.

## Rule 23 - Ownership Before Standardization

A common platform concept must not cause ownership of its implementation to move from the service that produces or controls the underlying data.

Common contracts define shared semantics and interoperability.

The producing service remains responsible for source-specific acquisition, hardware interaction, evidence creation, and source-specific operational behavior unless an explicit architectural decision establishes otherwise.

Standardize shared meaning before standardizing shared implementation.
