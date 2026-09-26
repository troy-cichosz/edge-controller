# AI Legal Edge Platform - Project Overview

**Document:** `projectoverview.md`  
**Purpose:** High-level platform map, architecture, development maturity, service roles, and summarized direction  
**Status:** Active  
**Version:** 1.3  
**Last major roadmap review:** September 2026

---

# 1. Purpose

This document is the high-level map of the AI Legal Edge Platform.

It answers:

- What are we building?
- Why does it exist?
- How is the platform organized?
- What are the major service roles?
- What is the current maturity?
- What architectural boundaries matter?
- What direction is the platform taking?

This document intentionally remains concise.

It does **not** serve as the detailed specification for evidence architecture, individual services, current lab deployment, project history, current sprint work, or the complete future capability list.

Those responsibilities belong to the documents identified in the documentation map below.

---

# 2. Ultimate Platform Objective

The ultimate objective is a distributed, local-first evidence acquisition and reconstruction platform for a physical vehicle and its surrounding environment.

A vehicle may contain multiple edge devices, with each device providing different capabilities such as:

```
video
audio
GNSS/GPS
vehicle telemetry
environmental sensors
switches/triggers
other future evidence sources
```

The platform preserves information locally, establishes a common temporal basis, maintains provenance and integrity, and eventually allows relevant information to be reconstructed around a selected time or event.

The eventual system should help answer:

> What happened during this period, where was the vehicle, what was it doing, what did the available sources observe, what did the system know about time, and can the provenance and integrity of the underlying information be independently examined?

The eventual user experience can present relevant evidence with synchronized playback and correlation where technically supportable. Detailed future presentation capabilities are maintained in `wishlist.md`.

The platform provides technical support for integrity, provenance, repeatability, and verifiability. It does **not** determine legal admissibility, evidentiary weight, or legal conclusions.

---

# 3. Platform Domain Model

The platform is a distributed evidence system rather than a collection of unrelated sensor services.

The long-term model is:

```
Vehicle
  |
  +-- Nodes
  |     |
  |     +-- Services
  |           |
  |           +-- Sensors / Sources
  |
  +-- Time System
  |
  +-- Evidence
  |
  +-- Observations
  |
  +-- Events
  |
  +-- Timeline
```

## Core Concepts

**Evidence** - An original or preserved data artifact produced by an evidence-producing service. Authoritative evidence is immutable after finalization.

**Observation** - Measured, detected, or reported information associated with a source and temporal context. An observation may reference evidence.

**Event** - A bounded context on the canonical timeline that groups related evidence, observations, and system activity.

**Timeline** - The temporal representation used to correlate heterogeneous sources while preserving time-source provenance and uncertainty.

Detailed definitions, relationships, and the common evidence model are maintained in `evidencearchitecture.md`.

---

# 4. Evidence Lifecycle

The intended platform flow is:

```
REAL-WORLD EVENT
      |
      v
DISTRIBUTED EDGE CAPTURE
      |
      v
IMMUTABLE SOURCE EVIDENCE
      |
      v
PROVENANCE / INTEGRITY / TEMPORAL CONTEXT
      |
      v
EVIDENCE / OBSERVATION / EVENT TIMELINE
      |
      v
VERIFICATION / CUSTODY
      |
      v
AI ANALYSIS
      |
      v
DERIVED OBSERVATIONS
      |
      v
SYNCHRONIZED RECONSTRUCTION
      |
      v
LEGAL / INVESTIGATIVE WORKFLOW
```

AI processing and presentation derivatives must not replace or silently modify authoritative source evidence.

---

# 5. Architecture Planes

The platform has two primary planes.

```
                    AI LEGAL EDGE PLATFORM
                              |
                +-------------+-------------+
                |                           |
         EVIDENCE PLANE                MANAGEMENT PLANE
                |                           |
        edge evidence services        edge-controller
                |                           |
       local evidence + time         discovery / policy
                                      configuration / calibration
                |
           local edge-time
                |
        common time context
```

## Evidence Plane

Evidence-producing services create and preserve source information locally or near the producing device.

Current examples:

```
edge-video
edge-audio
edge-gps
edge-time
```

Future evidence-producing services may include vehicle, sensor, discovery, or other source-specific services.

## Management Plane

`edge-controller` provides generic management, policy, discovery, observation, configuration, calibration coordination, and GUI functions. Audit logging for evidence-affecting management changes is an architectural requirement and future capability, not a currently implemented controller function.

The controller must not become a mandatory real-time evidence path or timestamp broker.

---

# 6. Time System

Time is a platform-wide dependency because heterogeneous evidence must be correlated without overstating temporal precision.

Evidence-producing services obtain temporal context from local `edge-time`.

The platform preserves distinctions between:

```
clock time
source observation
authority relationship
measurement uncertainty
synchronization state
holdover state
cryptographic attestation
```

The common evidence architecture defines how temporal context becomes part of evidence provenance.

The `edge-time` repository owns the service-specific time implementation and contract.

---

# 7. Repository Ecosystem

Current repositories:

```
edge-controller
edge-time
edge-gps
edge-audio
edge-video
```

Future services may include:

```
edge-vehicle
edge-sensor
edge-discovery
```

The platform is intentionally service-oriented. A node may host multiple services, and the controller discovers node/service relationships dynamically.

The repository branches and verification workflow are defined in `chatrules.md`.

---

# 8. Current Platform Maturity

The project is organized around the evidence lifecycle rather than independent repository completion.

## Phase 0 - Platform Foundation

**Status: Complete / Maintenance**

The generic controller/node/service foundation is operational, including dynamic service discovery, generic observations, host-addressed networking, and the management-plane foundation.

Detailed milestone history belongs in `projectstatus.md`.

## Phase 1 - Authoritative Time Foundation

**Status: Core operational; evidence-facing refinement remains**

The distributed `edge-time` authority/agent foundation and Capture Time Context are operational.

Remaining time-related work includes refinement and broader failure/authority behavior verification.

Detailed time implementation belongs in `edge-time`; development history belongs in `projectstatus.md`; current work belongs in `sprintstatus.md`.

## Phase 2 - Common Evidence Architecture

**Status: Current strategic priority**

The platform is establishing the common Evidence, Observation, Event, Timeline, provenance, integrity, manifest, attestation, and custody model before broad evidence integration.

The detailed architecture is maintained in `evidencearchitecture.md`.

---

# 9. Current Service Roles

## edge-controller

Generic management and policy plane.

Owns platform-level management state, discovery, generic observations, configuration coordination, calibration workflow state, and the current management GUI foundation. Audit logging remains a future platform capability.

It does not own source-specific hardware operations or mandatory real-time evidence capture.

## edge-time

Provides local temporal authority/agent functionality and Capture Time Context for evidence-producing services.

## edge-video

Evidence-producing video service.

The current MVP captures local video evidence and associates it with service-managed provenance and manifests. Multi-camera expansion is an architectural direction rather than a reason to make the controller camera-specific.

## edge-audio

Evidence-producing audio service.

It preserves source-specific audio provenance and participates in the common temporal/evidence architecture.

## edge-gps

Owns GNSS hardware and observations.

GNSS information contributes source observations and temporal/location context but remains distinct from derived platform time.

## Future evidence services

Vehicle telemetry, general sensors, device discovery, and other future capabilities should remain separate evidence-producing services when they have distinct hardware or source ownership.

Detailed future capabilities are maintained in `wishlist.md`.

---

# 10. Vehicle Context

The vehicle is a first-class platform context rather than merely another sensor.

Conceptually:

```
Vehicle
  |
  +-- Nodes
  |     |
  |     +-- Services
  |
  +-- Evidence
  |
  +-- Events
  |
  +-- Timeline
  |
  +-- Time system
  |
  +-- Vehicle telemetry
```

Vehicle identity, configuration, telemetry, and provenance should remain distinguishable from the identity of individual edge nodes.

A future `edge-vehicle` service is expected to own vehicle/OBD-II hardware interactions rather than placing those operations in `edge-controller`.

Detailed vehicle capabilities remain in `wishlist.md`.

---

# 11. Reconstruction and Presentation

A major long-term platform capability is synchronized reconstruction of a selected event or time interval.

The reconstruction layer is downstream of source evidence preservation:

```
source evidence
      |
      v
temporal/provenance model
      |
      v
correlation
      |
      v
reconstruction / presentation
```

It may eventually correlate video, audio, GNSS, vehicle telemetry, sensors, system events, transcripts, and derived observations.

Presentation artifacts are derivatives. The authoritative source evidence remains separately preserved and verifiable.

Detailed future presentation capabilities are maintained in `wishlist.md`.

---

# 12. Integrity, Provenance, and Derived Information

The platform is designed to preserve:

```
source identity
capture context
time provenance
uncertainty
location/context
configuration
calibration
content integrity
attestation
derivative relationships
custody history
```

A cryptographic hash or signature is part of a broader provenance model; it is not the entire evidence model.

AI analysis, synchronization, transcription, OCR, computer vision, overlays, reports, and other processing create derived information. Derived results must retain source relationships and applicable uncertainty.

Detailed evidence architecture is maintained in `evidencearchitecture.md`.

The platform provides technical mechanisms for preservation and verification; it does not determine legal admissibility.

---

# 13. Controller Boundary

`edge-controller` is the management and policy plane.

Its current responsibilities include:

```
node/service discovery
status
capabilities
generic observations
configuration
calibration coordination
time observability
evidence observability
policy
GUI
```

Audit logging is a future platform capability and is not currently implemented by the controller.

Its responsibilities do **not** include:

```
real-time evidence transport
timestamp brokering
source-specific hardware control
replacement for evidence-producing services
```

This boundary is an architectural invariant and is also defined by `projectrules.md`.

---

# 14. Current Direction

The current development direction is:

```
local edge-time
      |
      v
evidence-producing service
      |
      v
local evidence + temporal provenance
      |
      v
common evidence architecture
      |
      v
cross-source integration
      |
      v
reconstruction / analysis
```

Current live work is tracked in `sprintstatus.md`.

Major development history and significant decisions are tracked in `projectstatus.md`.

Future capabilities that have not been promoted into active development are tracked in `wishlist.md`.

---

# 15. Documentation Map

Project-level documentation has deliberately separated responsibilities:

| Document | Primary purpose |
|---|---|
| `projectoverview.md` | High-level platform map, architecture, service roles, maturity, and direction |
| `projectrules.md` | Enduring architectural and engineering invariants |
| `projectstatus.md` | Highest-level project development status, significant milestones, decisions, and development history |
| `sprintstatus.md` | Current project sprint lifecycle, work, status, blockers, next actions, and handoff |
| `wishlist.md` | Desired future capabilities not yet committed to active development |
| `envinfo.md` | Current development/lab environment and deployment facts |
| `chatrules.md` | Development, verification, recovery, and documentation workflow |
| Service `servicestatus.md` | Current service development phase, maturity, verified state, limitations, and remaining service-level work |
| Service `sprintstatus.md` | Current service sprint lifecycle, active work, verification requirements, and handoff |
| Service `README.md` / docs | Service-specific architecture, interfaces, configuration, operation, and troubleshooting |
| `evidencearchitecture.md` | Common evidence, temporal context, provenance, integrity, event, observation, and reconstruction model |

The overview should link to these documents rather than reproduce their detailed contents.

---

# 16. Architectural Direction

The platform should continue to grow by adding independently owned evidence-producing services behind a stable common evidence and temporal model.

The intended direction is:

```
many nodes
    +
many services
    +
many evidence sources
    +
common temporal context
    +
common provenance/integrity model
    +
generic management
    =
distributed evidence platform
```

The platform should remain local-first, service-oriented, hardware-agnostic at the controller layer, and explicit about uncertainty and provenance.

Detailed future capabilities remain in `wishlist.md` and should be promoted into active development only when their dependencies and verification requirements are established.
