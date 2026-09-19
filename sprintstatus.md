# edge-controller — Sprint Status

**Current sprint:** Platform foundation / maintenance transition  
**Status:** COMPLETE — maintenance-level foundation  
**Development phase:** Phase 0 complete

## Sprint Objective

Maintain and verify the generic controller/node/service foundation while downstream evidence and temporal services advance.

## Completed

- Generic node/service architecture
- Dynamic multi-service node handling
- Service registration and discovery
- Generic capabilities and observations
- Service configuration retrieval/update
- Service status handling
- Calibration job coordination
- Host-addressed service communication
- Initial management GUI foundation
- Controller management/policy boundary
- Development-only node data reset utility with safe stop-before-purge behavior; runtime verified on `pi4SSD`

The development reset verification also established that a clean node state can recreate required edge-time state and return the running edge services to normal operation. The reset remains a local development utility; controller/GUI-managed service-specific purge is future work.

## Current Work

No controller-specific implementation increment is currently blocking the platform.

Controller remains available as the generic management plane while active development moves through evidence-producing services and the common evidence architecture.

## Deferred

- Controller-managed time configuration
- Authority assignment and failover policy
- Audit logging for evidence-affecting management changes
- Generic calibration refinement
- Further generic management/GUI capabilities
- Controller/GUI-managed data lifecycle and service-specific purge operations

## Handoff

The next active platform work is evidence-facing temporal integration and common evidence architecture. Controller changes should be introduced only when required by a verified platform or service requirement.
