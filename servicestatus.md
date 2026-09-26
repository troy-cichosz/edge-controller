# edge-controller - Service Status

**Purpose:** Current development phase and maturity of the Edge Controller service.  
**Status:** Active / maintenance-level foundation  
**Last reviewed:** September 2026

## Current Phase

**Phase 0 - Platform Foundation: COMPLETE / MAINTENANCE**

The generic controller foundation is operational and is no longer the primary development focus.

It provides the management-plane foundation for node/service registration, dynamic multi-service relationships, discovery, status, generic capabilities and observations, configuration, calibration coordination, and the management GUI foundation.

The controller is not the mandatory real-time evidence path, timestamp broker, or owner of source evidence.

## Current Architectural Boundary

The controller owns management and policy coordination.

It does not perform real-time time calculation, broker Capture Time Context between evidence services and edge-time, capture or own source evidence, perform source-specific hardware operations, or replace evidence-producing services.

Audit logging for evidence-affecting management changes is an architectural requirement and future capability, not a currently implemented controller function.

## Current Development Position

The generic observation foundation is complete. Configuration and calibration coordination are operational foundations. The GUI continues to evolve toward generic service/resource handling, while service-specific presentation may remain where a service exposes specialized controls.

Future controller work is driven by platform needs rather than by expanding the controller into an evidence-processing service.

## Future / Deferred

Controller-managed time configuration, authority assignment/failover policy, audit logging, completion/refinement of generic calibration, and further generic management capabilities remain future work.

Detailed future scope belongs in `wishlist.md`; active work belongs in `sprintstatus.md`; enduring boundaries belong in `projectrules.md`.
