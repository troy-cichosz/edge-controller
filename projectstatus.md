# Development Priorities

The current priority sequence is:

1. Preserve the generic node/service architecture.
2. Preserve generic service capabilities and observation resources.
3. Use generic observation to expose `edge-time` operational information.
4. Establish the `edge-time` authority/time/source model.
5. Verify time consistency and failure behavior across all current nodes.
6. Validate and align the common evidence model across `edge-video` and `edge-audio`.
7. Establish the common evidence model across additional evidence-producing services.
8. Implement controller-managed time configuration.
9. Implement authority assignment and failover policy.
10. Add audit logging for evidence-affecting management changes.
11. Complete the generic calibration workflow.
12. Extend the same generic management model to other edge services.

The ordering is intentional.

The evidentiary time foundation must be validated before adding management controls capable of changing time policy.

---

# Platform Milestone History

## Platform Foundation

The initial platform foundation established the generic controller/node/service architecture, PostgreSQL-backed management state, dynamic multi-service node handling, service registration and discovery, generic observations, host-addressed service communication, and the initial management GUI foundation.

The controller foundation is now maintenance-level platform infrastructure rather than the primary development focus.

## Authoritative Time Foundation

The distributed `edge-time` architecture established a platform time authority with local agents on evidence-producing nodes.

The foundation includes source observations, authority relationships, uncertainty/freshness concepts, synchronization state, temporal provenance, cryptographic identity/attestation, and the Capture Time Context used by evidence-producing services.

The time foundation is operational, while broader failure/authority behavior and future management controls remain future work.

## Evidence-Facing Temporal Integration

Capture Time Context integration has been completed and verified in `edge-audio` and `edge-video`.

Both services obtain temporal context directly from their local `edge-time` instance and associate that context with their evidence provenance/manifest without making `edge-controller` part of the real-time capture path.

The project is now moving from service-specific temporal integration toward validation and alignment of the common evidence architecture across evidence-producing services.

## Current Evidence Architecture Transition

The project is transitioning from service-specific temporal integration toward a common evidence architecture covering:

```
Evidence
Observation
Event
Timeline
Provenance
Integrity
Attestation
Manifest
Custody
Derived information
Reconstruction
```

The detailed conceptual model is maintained in `evidencearchitecture.md`.

Current work and handoff state remain in `sprintstatus.md`.

---

# Significant Architectural Decisions

## Controller Boundary

`edge-controller` remains the management and policy plane.

It is not the mandatory real-time evidence path, timestamp broker, or replacement for evidence-producing services.

## Local Temporal Context

Evidence-producing services obtain temporal context directly from local `edge-time`.

The controller does not sit between an evidence producer and its local time service.

## Evidence Locality

Authoritative evidence is created and preserved on or near the producing device.

Central copies may exist for reference, backup, indexing, correlation, presentation, or processing, but they do not silently become the original.

## Provenance and Uncertainty

Evidence and derived information must retain source identity, temporal provenance, and applicable uncertainty.

The platform must not imply precision or certainty unsupported by the underlying source information.

---

# Time Failure and Holdover

Before powerful controller-managed time policy is enabled, test:

```
authority available/unavailable
GNSS available/unavailable
NTP available/unavailable
RTC available/unavailable
source freshness expiration
uncertainty threshold exceeded
authority holdover
controller unavailable
```

Holdover must distinguish:

```
fresh authoritative time
```

from:

```
held-over time
```

and eventually expose:

```
holdover active
holdover start
last authoritative observation
age
estimated uncertainty
```


## Development Status Hierarchy

The project-level development hierarchy is:

```
projectstatus.md   → highest-level project development state/history
        |
        +-- project sprintstatus.md → current platform sprint lifecycle
        |
        +-- service servicestatus.md → current service phase/maturity
        |
        +-- service sprintstatus.md → current service sprint lifecycle
```

Service-specific phase and maturity belong in each service's `servicestatus.md`. Active service development belongs in that service's `sprintstatus.md`. The project `projectstatus.md` records only development state and history significant at the platform level.

The retired `chatgpt.md` handoff documents are not part of the maintained documentation hierarchy.
