# edge-controller

Central management and orchestration service for the AI Legal Edge platform.

`edge-controller` provides the management plane for Raspberry Pi and other edge nodes running independently deployable services such as `edge-audio`, `edge-video`, `edge-gps`, and `edge-time`.

The controller is intentionally **service-agnostic**. A node may host multiple services, and the controller discovers and manages those services dynamically.

The controller is a management and policy plane. It is **not** the real-time evidence path and must not become the real-time timestamp provider for evidence-producing services.

---

# Current Status

The current development baseline provides:

* Containerized controller deployment
* FastAPI/Uvicorn application
* PostgreSQL-backed management state
* Node registration
* Node status tracking
* Service registration
* Per-node service discovery
* Generic multi-service node relationships
* Raspberry Pi ARM64 clients communicating with the controller
* Generic service endpoint registration
* Generic read-only service observation
* Configurable node hostname resolution
* Initial calibration database model
* Initial calibration implementation
* `edge-time` registration on both current Pi nodes
* Dynamic display of registered services under nodes

Current managed edge nodes include:

* `pi4SSD`
* `pi4nVME`

Both currently report their registered services to the controller.

The controller does not hard-code the service list. Services are discovered dynamically from the node/service model.

## Verified Service Relationships

Current registered service relationships include:

```text
pi4SSD
├── edge-audio
├── edge-gps
├── edge-time
└── edge-video

pi4nVME
├── edge-audio
├── edge-gps
├── edge-time
└── edge-video
```

The actual service list must always be discovered from the controller. It must not be hard-coded into the GUI.

## Generic Service Observation

The controller now supports read-only observation of a registered service through its registered endpoint.

Observation is generic and is not specific to `edge-time`.

The controller:

1. Retrieves the service's registered endpoint metadata.
2. Resolves the hosting node address.
3. Performs an HTTP GET against the registered service endpoint.
4. Records reachability and HTTP status.
5. Returns the service response when available.
6. Reports the hostname-resolution mode and attempted addresses.
7. Does not use Docker container/service names for inter-service HTTP.

The observation layer is management-plane functionality. It does not become part of the evidence-producing service's real-time data path.

## Node Host Resolution

Service endpoints are constructed from the registered node hostname and the service's exposed host port.

Host resolution is configurable through:

```text
EDGE_NODE_HOST_MODE
EDGE_NODE_DOMAIN
```

Supported modes are:

```text
short
domain
auto
```

### `short`

Use the registered hostname directly:

```text
pi4SSD
```

This mode is appropriate for environments where short-name resolution is available without a DNS domain.

### `domain`

Append the configured domain:

```text
pi4SSD.spoocannon.com
```

The domain is supplied through:

```text
EDGE_NODE_DOMAIN=spoocannon.com
```

### `auto`

Try the short hostname first and then the configured FQDN if a domain is available.

This is the default mode:

```text
EDGE_NODE_HOST_MODE=auto
```

For example:

```text
pi4SSD
    |
    +-- short hostname attempt
    |
    +-- pi4SSD.spoocannon.com
```

This permits the same controller implementation to operate in both managed DNS environments and deployments where no domain is available, including future vehicle/mobile deployments.

Node identity and network addressing remain separate concepts. The registered `node_id` does not change based on which hostname candidate is used.

## Host-Addressed HTTP Rule

Inter-service HTTP must use:

```text
<node-host>:<exposed-host-port>
```

Never use Docker container names or Docker Compose service names as cross-service endpoints.

Example:

```text
http://pi4SSD.spoocannon.com:8095/health
```

rather than:

```text
http://edge-time:8095/health
```

This rule allows services to communicate across Docker boundaries, physical hosts, VLANs, local networks, and future mobile/vehicle deployments.

## Current Read-Only Observation State

The controller has now successfully demonstrated host-addressed observation of `edge-time`.

For the current development environment:

```text
EDGE_NODE_HOST_MODE=auto
EDGE_NODE_DOMAIN=spoocannon.com
```

The short hostname is attempted first. Where short-name resolution is unavailable from the controller container, the configured FQDN is attempted and successfully reaches the service.

A successful observation contains:

```text
service identity
registered version
node identity
observed timestamp
selected endpoint
host-resolution mode
host-resolution attempts
reachability
HTTP status
content type
service response
```

This establishes the generic observation foundation.

The next step is not service-specific controller logic. The next step is to expand the generic observation/capability model so services can advertise which read-only operational information they expose.


---

# Architecture

The controller sits between edge services and the management interface:

```text
                    +----------------------+
                    |   edge-controller    |
                    |                      |
                    |  Node management     |
                    |  Service discovery   |
                    |  Configuration       |
                    |  Policy              |
                    |  Calibration         |
                    |  Audit               |
                    +----------+-----------+
                               |
                 +-------------+-------------+
                 |                           |
           +-----+-----+               +-----+-----+
           |  pi4SSD  |               | pi4nVME |
           +-----+-----+               +-----+-----+
                 |                           |
        +--------+--------+         +--------+--------+
        |        |        |         |        |        |
     audio    video     time      audio    video     time
                          |                         |
                       edge-gps                  edge-gps
```

A node is not limited to one service.

The controller's generic model is:

```text
Node
 └── Service
      ├── status
      ├── version
      ├── capabilities
      ├── configuration
      └── supported actions
```

Service-specific behavior belongs in the service itself.

---

# Node and Service Model

Nodes have a persistent internal UUID and a logical `node_id`.

The current database model includes:

```text
nodes
-----
id
node_id
hostname
platform
status
created_at
updated_at
```

Services are associated with nodes through the node UUID:

```text
services
--------
id
service_id
node_id
name
version
status
created_at
updated_at
```

A service is uniquely identified within a node by:

```text
(node_id, service_id)
```

This permits the same service to run on multiple nodes.

---

# Generic Service Registration

The common registration model uses:

```text
EDGE_CONTROLLER_URL
EDGE_NODE_ID
EDGE_SERVICE_ID
EDGE_SERVICE_NAME
EDGE_SERVICE_VERSION
```

The controller must continue to treat all services generically.

Adding a service must not require a new controller database model unless the service introduces a demonstrated management-plane requirement that cannot be represented through the generic model.

---

# edge-time Integration

`edge-time` is now a verified registered service on both Pi nodes.

```text
pi4SSD  -> edge-time -> edge-controller
pi4nVME  -> edge-time -> edge-controller
```

This integration is management-plane functionality.

The controller must not replace the local `edge-time` service as the source of real-time evidence timestamps.

The intended relationship is:

```text
                    edge-controller
                           |
                 management / policy
                           |
              +------------+------------+
              |                         |
         pi4SSD edge-time        pi4nVME edge-time
              |                         |
         local time                 local time
              |                         |
          evidence                 evidence
```

The controller may query and manage the time services, but evidence-producing services should obtain their actual timing context directly from their local `edge-time` service.

---

# Current edge-time Management Objective

The next controller milestone is to expose the operational state of `edge-time`.

The controller should be able to display, at minimum:

## Platform Time

* Current authoritative platform time
* Current local edge time
* UTC timestamp
* Monotonic timestamp where available
* Synchronization state
* Time uncertainty
* Observation freshness

## Authority

* Current platform authority
* Authority identity
* Authority role
* Authority endpoint
* Authority state
* Authority's selected local source
* Authority provenance

## Edge Source Selection

For every `edge-time` agent:

* Selected source
* Source priority
* Available sources
* Validity of each source
* Source observation timestamp
* Source uncertainty
* Source freshness
* Fallback/holdover state

## Time Relationship

The controller should eventually be able to show:

```text
platform authority
        |
        +-- selected source
        |
        +-- authority time
                 |
                 +-- pi4SSD edge-time
                 |
                 +-- pi4nVME edge-time
```

and identify the measured time relationship between nodes.

---

# Evidence-Time Objective

The purpose of this work is not merely to display a clock.

The objective is to establish a verifiable time/provenance chain for evidence.

The desired chain is:

```text
Evidence
   |
   v
Evidence-producing service
   |
   v
Local edge-time
   |
   +-- selected source
   |
   +-- source observation
   |
   +-- uncertainty
   |
   +-- freshness
   |
   +-- authority identity
   |
   v
Platform authority
   |
   v
Underlying authoritative source
```

An eventual evidence record should therefore be capable of establishing:

```text
what was recorded
when it was recorded
which device recorded it
which time service supplied the time
which source the time service selected
which authority supplied that source
what uncertainty existed
whether the source was fresh
what the synchronization state was
```

The controller should manage and audit this architecture but should not sit in the timestamp path for every evidence event.

---

# Read-Only Time Integration

The first `edge-time` controller milestone should be **read-only**.

Before allowing the controller to change time configuration, the controller must successfully retrieve and display the operational state from each `edge-time` instance.

The first integration should therefore use the existing service API to retrieve:

```text
/health
/status
/time
/time/sources
/time/attestation
/authority
```

Where applicable, the authority endpoint may also be queried:

```text
/authority/time
```

The controller should not initially modify these services.

---

# Time Configuration and Policy

After read-only integration is verified, the controller may become the management authority for permitted time configuration.

Potential management functions include:

* Assign platform authority
* Remove authority assignment
* Change authority endpoint
* Configure authority identity
* Change source priority
* Enable/disable permitted time sources
* Configure maximum acceptable uncertainty
* Configure freshness thresholds
* Configure holdover policy
* Configure authority failover policy

These actions must be treated as **management-plane configuration**, not as direct manipulation of the time engine's internal state.

---

# Authority Policy

`edge-time` does not independently elect arbitrary platform authorities.

The controller is the appropriate future owner of platform authority policy.

Potential controller responsibilities include:

```text
authority eligibility
authority assignment
authority promotion
authority removal
authority failover
authority policy
```

The actual time calculation remains inside `edge-time`.

Authority changes must be:

1. Explicit.
2. Validated.
3. Persisted.
4. Audited.
5. Propagated to the affected service.
6. Verified after application.

---

# Audit Requirements

Management-plane changes affecting evidence timing must be auditable.

An eventual audit record should include:

```text
event_id
event_time
actor
node_id
service_id
operation
previous_value
new_value
result
error
```

The event itself should use the platform's established evidence-time/provenance model.

The controller must not silently change authority or source configuration.

---

# Generic Capabilities

The controller should evolve toward a generic service capability model.

A service may advertise capabilities such as:

```text
service.capabilities
    status
    configuration
    calibration
    time
    authority
    evidence
    diagnostics
```

The GUI should use these capabilities to determine what controls and information are available.

Do not implement:

```text
if service == "edge-time"
```

throughout generic GUI or controller logic.

`edge-time` is the first service that will exercise richer capabilities.

---

# Calibration

Calibration remains part of the controller architecture, but it is no longer the sole immediate development priority.

The controller owns:

* Calibration job creation
* Job persistence
* Job assignment
* Job state
* Job result
* Job error

The edge service owns:

* Hardware measurement
* Calibration calculation
* Physical operation

The controller remains hardware-agnostic.

The existing calibration model is:

```text
calibration_jobs
----------------
id
node_id
service_id
status
duration_seconds
result
error
created_at
updated_at
```

Calibration development should continue after the generic service-management foundation is established.

---

# Database

PostgreSQL is the controller's durable management-state store.

Use PostgreSQL for:

* nodes
* services
* configuration state
* calibration jobs
* authority policy
* management events
* audit records
* future management-plane state

Do not introduce another database unless there is a demonstrated architectural requirement.

---

# API Direction

The existing node/service API includes:

```text
GET /api/v1/nodes/{node_id}
GET /api/v1/nodes/{node_id}/services

POST /api/v1/nodes
POST /api/v1/nodes/{node_id}/services

PUT /api/v1/nodes/{node_id}/services/{service_id}/status
```

Future APIs should preserve the generic service model.

The next API work should support:

```text
service status
service capabilities
service observations
service configuration
service actions
management/audit events
```

Time-specific routes should be exposed through a generic service-management architecture where practical rather than embedding `edge-time` assumptions throughout the controller.

---

# GUI Direction

The GUI should dynamically discover:

```text
Nodes
  |
  +-- Services
        |
        +-- Capabilities
        |
        +-- Status
        |
        +-- Configuration
        |
        +-- Actions
```

For `edge-time`, the GUI should eventually provide a dedicated time-management view because the information is operationally important.

Conceptually:

```text
TIME PLATFORM

Authority
  spoo-lin
  edge-time
  Source: NTP
  State: SYNCHRONIZED

Agents

pi4SSD
  Time: ...
  Source: authority
  Uncertainty: ...
  Freshness: ...
  State: SYNCHRONIZED

pi4nVME
  Time: ...
  Source: authority
  Uncertainty: ...
  Freshness: ...
  State: SYNCHRONIZED

Authority Chain
  spoo-lin
    └── NTP
        └── platform authority
            ├── pi4SSD
            └── pi4nVME
```

Configuration controls should initially be read-only.

Control operations should be enabled only after the read-only and evidence-integrity phases have been verified.

---

# Development Priorities

The current priority is:

1. Preserve the generic node/service architecture.
2. Expand generic service observation.
3. Establish a generic service capability declaration model.
4. Use capabilities to determine which read-only observations are available.
5. Integrate `edge-time` operational observations without hard-coding `edge-time` into generic controller logic.
6. Display authority, current edge time, source, uncertainty, freshness, and provenance.
7. Verify time consistency and failure behavior across all current nodes.
8. Establish the common evidence timestamp/provenance envelope.
9. Validate the envelope with `edge-video` and `edge-audio`.
10. Implement controller-managed time configuration.
11. Implement authority assignment and failover policy.
12. Add audit logging for all evidence-affecting management changes.
13. Complete the generic calibration workflow.
14. Extend the same generic management model to other edge services.

The ordering remains intentional.

The evidentiary time foundation must be validated before adding management controls capable of changing time policy.

---

# Architectural Rules

## Rule 1 — Generic Controller

Never hard-code a particular service into generic controller logic.

## Rule 2 — Dynamic Discovery

Nodes may host multiple services.

## Rule 3 — Hardware Separation

Hardware-specific operations belong in the corresponding edge service.

## Rule 4 — PostgreSQL

Durable controller management state belongs in PostgreSQL.

## Rule 5 — Container First

Controller and edge services remain containerized.

## Rule 6 — Host-Addressed HTTP

Inter-service HTTP uses the hosting node's hostname/IP and exposed host port.

Do not use Docker container/service names as cross-service endpoints.

## Rule 7 — Evidence Locality

The controller is not the real-time evidence path.

## Rule 8 — Local Time Service

Evidence-producing services obtain their timing context from local `edge-time`.

## Rule 9 — Controller Policy

The controller owns management policy, not real-time time calculation.

## Rule 10 — Audit

Changes affecting evidence integrity must be auditable.

## Rule 11 — Incremental Verification

Verify each end-to-end capability before adding another abstraction layer.

## Rule 12 — Source Before Assumption

Inspect actual current source before inventing routes, models, or behavior.

## Rule 13 — Runtime Completion

A feature is not complete until deployed containers demonstrate the expected behavior.

## Rule 14 — Documentation

Update `README.md` and `chatgpt.md` after meaningful architectural or operational changes.

---

# Current Handoff State

```text
Controller container:                 WORKING
PostgreSQL:                           WORKING
Controller API:                       WORKING
Node registration:                    WORKING
Node lookup:                          WORKING
Service registration:                 WORKING
Service discovery:                   WORKING
Service status updates:               WORKING

pi4SSD communication:                WORKING
pi4nVME communication:               WORKING

edge-audio registration:              VERIFIED
edge-gps registration:               VERIFIED
edge-time registration:              VERIFIED
edge-video registration:              VERIFIED

Generic multi-service model:          VERIFIED
Generic service endpoint model:       VERIFIED
Generic service observation:          VERIFIED

Node host resolution:                 VERIFIED
Short hostname resolution:            SUPPORTED
Domain/FQDN resolution:              SUPPORTED
Automatic short/FQDN fallback:       VERIFIED

edge-time version refresh:            VERIFIED
edge-time read-only health query:    VERIFIED

Generic capability model:             NEXT
Full edge-time observability:        NEXT
Time consistency validation:          NEXT
Evidence timestamp envelope:         NEXT

Authority management:                 FUTURE
Authority failover:                   FUTURE
Audit/event model:                    FUTURE

Calibration database model:           PRESENT
Calibration E2E:                      NOT COMPLETE

Evidence timestamp envelope:          NOT FINALIZED
Cross-service evidence integration:   NOT COMPLETE
```

---

# Next Development Session

The next controller development session should begin by inspecting the actual current source.

Do not begin by changing `edge-time`.

Determine:

```text
current API structure
current service model
current response models
current database model
current GUI implementation
current service registration behavior
```

Then design the smallest generic capability/observation layer required to retrieve `edge-time` information.

The first runtime objective is:

```text
edge-controller
      |
      +-- discover edge-time
      |
      +-- query edge-time
      |
      +-- persist management observation if appropriate
      |
      +-- display:
              authority
              edge time
              source
              uncertainty
              freshness
              state
              provenance
```

Only after that is verified should configuration-changing operations be introduced.
