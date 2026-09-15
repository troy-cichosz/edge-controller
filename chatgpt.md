# edge-controller — ChatGPT Development Handoff

# Current Handoff Update — 2026-09-15

This section is authoritative for the current development state and supersedes older sections that describe the controller as lacking generic service observation or node hostname-resolution support.

## Current Controller State

The current public GitHub source has been reviewed and verified.

The controller currently provides:

```text
node registration
node lookup
node status
generic service registration
generic service discovery
generic service status
generic service endpoint registration
generic service observation
configurable node hostname resolution
```

The controller remains service-agnostic.

A node may host multiple independently deployed services. The controller must not introduce service-specific controller logic merely because a particular service is currently being integrated.

## Generic Service Observation

The controller now supports read-only observation of a registered service.

The observation path:

```text
Controller
    |
    +-- registered node
    |
    +-- registered service
    |
    +-- registered endpoint
    |
    +-- resolve node host
    |
    +-- HTTP GET
    |
    +-- return observation
```

Observation includes:

```text
service identity
service version
node identity
observation timestamp
endpoint
host-resolution mode
host-resolution attempts
selected host
reachability
HTTP status
content type
service response
```

This is management-plane observation only.

It must not become part of the real-time evidence path.

## Node Host Resolution

The controller now supports:

```text
EDGE_NODE_HOST_MODE=short
EDGE_NODE_HOST_MODE=domain
EDGE_NODE_HOST_MODE=auto
```

and:

```text
EDGE_NODE_DOMAIN=<domain>
```

`auto` is the default.

In `auto` mode:

```text
registered hostname
       |
       +-- short hostname
       |
       +-- configured FQDN
```

The controller records each attempted address and identifies the selected address in the observation response.

This permits operation in:

* DNS-managed development/lab environments
* networks with short-name resolution
* environments requiring FQDNs
* future mobile/vehicle deployments where no domain may exist

The node's logical identity remains independent of its network address.

## Verified Current Deployment

Current managed nodes:

```text
pi4SSD
pi4nVME
```

Current service relationships:

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

The current controller deployment has been configured with:

```text
EDGE_NODE_HOST_MODE=auto
EDGE_NODE_DOMAIN=spoocannon.com
```

The controller successfully reaches the Pi-hosted `edge-time` service using the configured FQDN fallback when short-name resolution is unavailable inside the controller container.

## edge-time Registration Refresh

`edge-time` registration is now idempotent.

A service that is already registered is not silently skipped.

Each registration refreshes:

```text
service_id
name
version
endpoint scheme
endpoint port
endpoint path
```

This ensures that a newly deployed service version is reflected in the controller without requiring deletion and recreation of the service record.

The current deployed `edge-time` build verified during this development session is:

```text
0.2.2-20260915.7
```

## Current Development Boundary

The controller now has the foundation required for generic read-only service observability.

The next implementation should therefore NOT:

```text
hard-code edge-time routes throughout controller logic
add edge-time-specific database structures
move time calculation into the controller
make the controller the evidence timestamp source
```

Instead, the next abstraction should be:

```text
generic service capabilities
        |
        +-- observable endpoints
        +-- status
        +-- diagnostics
        +-- configuration
        +-- actions
```

`edge-time` can then advertise its own operational capabilities through the generic model.

## Current Next Steps

```text
1. Expand generic service observation.

2. Establish generic service capabilities.

3. Expose edge-time read-only operational information
   through the generic capability model.

4. Verify:
      authority
      current time
      source
      uncertainty
      freshness
      synchronization state
      provenance

5. Validate time relationships across:
      spoo-lin
      pi4SSD
      pi4nVME

6. Establish the common evidence timestamp/provenance envelope.

7. Integrate the envelope with edge-video and edge-audio.

8. Only then introduce controller-managed time policy.

9. Add auditable authority assignment/failover.

10. Continue generic calibration work.
```

## Important Documentation Rule

After each successfully deployed feature, update:

```text
README.md
chatgpt.md
```

The documentation must distinguish:

```text
implemented in source
deployed
runtime verified
planned
future
```

A feature is not considered complete merely because the source exists. Runtime behavior must be verified on the deployed containers.


## Purpose

This document is the authoritative continuation point for future ChatGPT sessions working on `edge-controller` in the AI Legal Edge platform.

`edge-controller` is the central management and policy plane for edge nodes and independently deployable services.

The controller must remain generic.

A node may host multiple services. The controller must never assume that `edge-audio`, `edge-video`, `edge-gps`, or `edge-time` is the only service hosted by a node.

---

# 1. Current Development State

Repository:

```text
D:\src\edge-controller
```

Development is performed through Azure DevOps.

Public GitHub:

```text
https://github.com/troy-cichosz/edge-controller
```

When ADO/local state and public GitHub differ:

1. Explicitly supplied and tested ADO/local state is authoritative.
2. Public GitHub represents the last synchronized public source.
3. Do not assume GitHub contains unsynchronized ADO changes.

Current public repository state confirms the generic node/service architecture and working service registration.

---

# 2. Deployment

Controller host:

```text
spoo-lin
```

Deployment:

```text
/data/services/edge-controller
```

Controller container:

```text
edge-controller
```

PostgreSQL:

```text
controller-postgres
```

Controller API:

```text
0.0.0.0:8080
```

---

# 3. Architectural Role

The controller owns the management/policy plane:

```text
node management
service discovery
service registration
service status
configuration
policy
calibration
authority management
audit
future GUI/API management
```

The controller does NOT own:

```text
real-time evidence capture
hardware operation
real-time timestamp generation
GNSS acquisition
microphone acquisition
camera acquisition
```

The relevant edge service owns the physical or real-time operation.

---

# 4. Verified Nodes

Current managed edge nodes:

```text
pi4SSD
pi4nVME
```

Both communicate with the controller and report service state.

`spoo-lin` hosts:

```text
edge-controller
edge-time ROLE=authority
```

`spoo-lin` does not need to be registered as a managed edge node merely because it hosts the controller.

---

# 5. Verified Services

Current verified service relationships:

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

This is an important architectural verification.

The controller is correctly modeling multiple services per node.

The GUI must derive this relationship dynamically.

---

# 6. edge-time Integration

`edge-time` is now a verified controller-registered service.

Verified:

```text
pi4SSD -> edge-time -> controller
pi4nVME -> edge-time -> controller
```

The service currently reports version:

```text
0.3.0
```

Registration is generic and does not require an edge-time-specific database structure.

The controller integration is management-plane functionality only.

`edge-time` must continue operating if the controller is unavailable.

---

# 7. Current edge-time Architecture

Current platform:

```text
spoo-lin
  edge-time ROLE=authority :8095
        |
        +----------------------+
        |                      |
        v                      v
pi4SSD edge-time agent   pi4nVME edge-time agent
        |                      |
   edge-gps :8096          edge-gps :8096
```

Current source priorities:

```text
spoo-lin:
    ntp,rtc,system

pi4SSD:
    authority,gnss,rtc,ntp,system

pi4nVME:
    authority,gnss,rtc,ntp,system
```

Verified:

* `spoo-lin /authority/time` returns HTTP 200.
* `spoo-lin` selects NTP.
* `pi4SSD` selects the platform authority even when local GNSS is valid.
* `pi4nVME` selects the platform authority while GNSS has no valid fix.
* `edge-gps` remains independently responsible for GNSS acquisition.
* Both Pi nodes register `edge-time` with the controller.
* Controller status reporting works.
* The previous repeated-registration problem is resolved.

---

# 8. New Controller Development Direction

The previous controller priority list placed calibration first.

That is no longer the preferred immediate sequence.

The next controller milestone is:

```text
GENERIC SERVICE OBSERVABILITY
        |
        v
EDGE-TIME READ-ONLY INTEGRATION
        |
        v
EVIDENCE TIME VALIDATION
        |
        v
TIME MANAGEMENT / POLICY
        |
        v
AUDITABLE CONTROL
```

Calibration remains required, but should follow the generic management foundation.

The reason is architectural: `edge-time` is now operational and registered, and its output is foundational to every future evidence-producing service.

---

# 9. First edge-time Controller Goal

The first implementation should be read-only.

The controller should retrieve operational state from every registered `edge-time` service.

The initial data set should include:

```text
device/node identity
service identity
service version

current UTC time
current monotonic time, if exposed
selected source
synchronization state
uncertainty
freshness

authority identity
authority role
authority endpoint
authority state
authority selected source

individual source observations
source validity
source timestamp
source uncertainty

attestation information
```

Existing edge-time API surfaces include:

```text
GET /health
GET /status
GET /time
GET /time/sources
GET /time/attestation
GET /authority
GET /authority/time
```

The controller should consume these through the registered service's host address and exposed port.

---

# 10. Time Observability Model

The controller should provide a platform-level representation similar to:

```text
TIME PLATFORM

Authority
  spoo-lin
  edge-time
  source: NTP
  state: SYNCHRONIZED

Agents

pi4SSD
  edge-time
  selected source: authority
  state: SYNCHRONIZED
  uncertainty: ...
  freshness: ...

pi4nVME
  edge-time
  selected source: authority
  state: SYNCHRONIZED
  uncertainty: ...
  freshness: ...
```

The controller should also calculate or display useful cross-node relationships:

```text
authority time
        |
        +-- pi4SSD time
        |
        +-- pi4nVME time
```

The objective is to identify whether all evidence-capable nodes are operating against a common, sufficiently fresh and sufficiently precise time basis.

---

# 11. Evidentiary Time Objective

The purpose of `edge-time` is not merely to provide a UTC clock.

The intended evidence chain is:

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
  +-- source observation
  +-- uncertainty
  +-- freshness
  +-- synchronization state
  +-- authority identity
  |
  v
Platform authority
  |
  v
Underlying authoritative source
```

This information should eventually accompany evidence metadata.

For example:

```text
evidence_id
device_id
capture_timestamp_utc
capture_monotonic
time_service
selected_source
authority_id
source_timestamp
uncertainty
freshness
synchronization_state
attestation
evidence_hash
manifest_id
```

This is the direction for a common evidence timestamp/provenance envelope.

The controller must not become the real-time timestamp broker.

---

# 12. Evidence Integrity

The controller's objective is to make the timing architecture:

```text
observable
verifiable
auditable
reproducible
```

It must be possible to answer after an incident:

```text
What time was assigned?

Which service supplied that time?

Which source was selected?

Was that source valid?

How fresh was it?

What uncertainty existed?

Which authority supplied it?

What source was the authority using?

Had the authority changed?

Had the node entered holdover?

Was the configuration subsequently modified?
```

This is more important than simply displaying a clock in the GUI.

The timing architecture itself does not automatically make evidence legally admissible. It provides technical provenance, synchronization, integrity, and auditability that can support later evidentiary validation.

---

# 13. Failure Testing Before Control

Before implementing configuration-changing controls, test:

```text
authority available
authority unavailable
local GNSS valid
local GNSS unavailable
local NTP available
local NTP unavailable
multiple sources available
only fallback source available
authority holdover
source freshness expiration
uncertainty threshold exceeded
controller unavailable
```

The controller should observe these conditions without becoming part of the timing path.

Expected behavior should be recorded and verified.

---

# 14. Controller-Managed Time Policy

After read-only observability and failure behavior are verified, the controller may become the policy owner for:

```text
authority eligibility
authority assignment
authority promotion
authority removal
authority failover
source priority
allowed sources
freshness policy
uncertainty policy
holdover policy
authority endpoint
```

The controller must not calculate or manufacture the actual time.

`edge-time` remains responsible for time selection and time response.

---

# 15. Authority Changes

Changing authority is a high-impact management operation.

It must not be implemented as an uncontrolled HTTP request from the GUI.

The eventual workflow should be:

```text
GUI
 |
 v
Controller API
 |
 v
Validate requested authority
 |
 v
Persist intended policy
 |
 v
Apply configuration
 |
 v
Verify edge-time response
 |
 v
Record result
 |
 v
Audit event
```

A failed authority change must not silently leave the platform in an unknown state.

---

# 16. Source Priority Changes

The controller may eventually expose source priority configuration such as:

```text
authority
gnss
rtc
ntp
system
```

However, the controller should not allow arbitrary unsafe configurations without validation.

Examples of policy checks:

* A source must be supported by the service.
* At least one valid fallback must remain.
* `system` should be treated as a degraded source.
* Authority configuration must identify a valid authority.
* Maximum uncertainty must remain within policy.
* Holdover behavior must be explicit.

---

# 17. Generic Capability Model

The controller should evolve toward generic service capabilities.

Conceptually:

```text
service
  |
  +-- capabilities
       |
       +-- status
       +-- configuration
       +-- calibration
       +-- diagnostics
       +-- evidence
       +-- time
       +-- authority
       +-- actions
```

The GUI should discover capabilities rather than use service-name conditionals everywhere.

`edge-time` is the first service that requires a richer capability/management interface.

---

# 18. GUI Direction

The GUI should dynamically discover:

```text
Nodes
  |
  +-- Services
        |
        +-- Status
        +-- Capabilities
        +-- Observations
        +-- Configuration
        +-- Actions
```

For the `edge-time` service, the GUI should eventually expose:

### Status

```text
current time
source
state
uncertainty
freshness
```

### Authority

```text
authority node
authority identity
authority source
authority state
```

### Sources

```text
authority
GNSS
RTC
NTP
system
```

with:

```text
validity
timestamp
uncertainty
freshness
```

### Provenance

```text
local source
authority
authority source
attestation
```

### Configuration

Initially read-only.

Later:

```text
authority
source priority
source enablement
freshness
uncertainty
holdover
```

---

# 19. Audit Requirements

All management operations affecting evidence integrity should generate durable audit records.

Minimum conceptual fields:

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

Examples:

```text
authority changed
source priority changed
authority URL changed
holdover policy changed
time source disabled
time source enabled
```

Audit records themselves require reliable time provenance.

---

# 20. Calibration

Calibration remains part of the controller architecture.

The existing model:

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

The controller owns:

```text
job creation
job persistence
job assignment
job state
job result
job error
```

The edge service owns:

```text
hardware measurement
calculation
physical operation
result submission
```

The first historical calibration target remains:

```text
pi4nVME
edge-audio
10 seconds
```

However, calibration is no longer the first feature to implement in the next development session.

---

# 21. Database Direction

PostgreSQL remains the controller's durable management-state store.

Use it for:

```text
nodes
services
configuration
calibration_jobs
authority policy
management events
audit records
```

Do not introduce Redis or another database without a demonstrated requirement.

---

# 22. Network Rule

Inter-service HTTP must use the hosting node's hostname/IP and exposed host port.

Correct:

```text
http://spoo-lin.spoocannon.com:8095/authority/time
http://pi4SSD:8095/time
http://pi4nVME:8095/time
```

Do not use Docker service/container names as cross-service endpoints.

---

# 23. Runtime Verification

A feature is not complete until it is verified in the deployed containers.

For edge-time/controller integration:

```text
source
  |
  v
build
  |
  v
container
  |
  v
deployment
  |
  v
controller discovery
  |
  v
runtime API query
  |
  v
GUI/API observation
  |
  v
failure testing
```

---

# 24. Current Handoff State

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
edge-gps registration:                VERIFIED
edge-time registration:               VERIFIED
edge-video registration:              VERIFIED

Generic multi-service model:          VERIFIED
edge-time GUI registration:            VERIFIED

Generic capabilities model:           NEXT
edge-time read-only observability:    NEXT
Time consistency testing:             NEXT
Evidence provenance validation:       NEXT

Authority management:                 FUTURE
Authority failover:                   FUTURE
Audit/event model:                    FUTURE

Calibration database model:            PRESENT
Calibration E2E:                       NOT COMPLETE

Evidence timestamp envelope:           NOT FINALIZED
Cross-service evidence integration:    NOT COMPLETE
```

---

# 25. Next Controller Development Session

Start by inspecting the actual current source.

Do not modify `edge-time` unless testing demonstrates an edge-time defect.

Determine:

```text
current API routes
request models
response models
service models
database models
current GUI implementation
service registration implementation
```

Then implement the smallest generic capability/observation mechanism necessary to query `edge-time`.

First successful milestone:

```text
Controller
  |
  +-- discovers edge-time
  |
  +-- queries edge-time
  |
  +-- receives current time
  +-- receives source
  +-- receives authority
  +-- receives uncertainty
  +-- receives freshness
  +-- receives state
  +-- receives provenance
  |
  v
GUI/API
```

Second milestone:

```text
authority + pi4SSD + pi4nVME
          |
          v
cross-node time comparison
          |
          v
evidence-time validation
```

Third milestone:

```text
validated time system
          |
          v
controller-managed configuration
          |
          v
auditable authority/source changes
```

Do not start with authority-changing controls.

First prove that the controller can accurately observe and report the existing time system.

---

# 26. Architectural Rules

1. **Generic controller** — never hard-code a service into generic logic.
2. **Dynamic discovery** — discover nodes and services dynamically.
3. **Hardware separation** — hardware operations belong to edge services.
4. **PostgreSQL** — durable controller state belongs in PostgreSQL.
5. **Container first** — controller and services remain containerized.
6. **Host-addressed HTTP** — use node hostname/IP and exposed host port.
7. **Evidence locality** — controller is not the real-time evidence path.
8. **Local time service** — evidence services obtain timing from local `edge-time`.
9. **Controller policy** — controller manages policy, not time calculation.
10. **Audit** — evidence-affecting configuration changes are auditable.
11. **Incremental verification** — prove each stage before advancing.
12. **Source before assumption** — inspect actual source before inventing APIs.
13. **Runtime completion** — deployed behavior is the acceptance criterion.
14. **Documentation** — update project MD files after meaningful architectural changes.
