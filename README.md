# edge-controller

Central management, discovery, and observation service for the AI Legal Edge platform.

edge-controller provides the platform management plane for distributed edge nodes and the independently deployable services hosted on those nodes.

The controller is intentionally **service-agnostic**:

- A node may host multiple services.
- A service may run on multiple nodes.
- Services declare management-plane capabilities and observation resources.
- The controller discovers and manages services through the generic node/service model.
- Service-specific behavior remains in the owning service.

The controller is **not** the real-time evidence path, evidence store, or real-time timestamp provider. Evidence-producing services communicate with their local edge-time service directly for temporal context.

## Responsibilities

The current controller provides management-plane functions for:

- Node registration and management
- Service registration and discovery
- Service status
- Generic capability declarations
- Generic read-only service observation
- Service endpoint metadata
- Service configuration storage
- Calibration workflow state

The controller does not take ownership of service-specific evidence, sensor measurements, time calculations, or other hardware-specific operations.

Future management capabilities may extend this model, but they should preserve the generic node/service architecture.

## Development Data Reset

The repository includes a development-only node reset utility:

~~~text
scripts/reset-node-data.sh
~~~

Run on a development node as:

~~~bash
sudo ./scripts/reset-node-data.sh --all
~~~

The utility is intentionally limited to disposable development data. It currently:

- Stops running containers whose names begin with `edge-`.
- Purges the shared `recordings`, `logs`, `metadata`, and `state` data roots under `EDGE_SERVICES_ROOT` (default `/data/services`).
- Truncates Docker JSON logs for `edge-` containers.
- Restarts containers that were running before the reset.
- Preserves service configuration and deployment files.

Use `--dry-run` to inspect the planned operation without changing data. Use `--yes` only when the destructive operation is intentionally being automated.

This is not a production evidence-retention, remote purge, service-state recovery, or factory-reset mechanism. Service-specific purge ownership and controller/GUI lifecycle management remain future capabilities described in `wishlist.md`.

The reset is deliberately fail-safe: if a running edge container cannot be stopped cleanly, the script exits before purging the shared data. During development verification on `pi4SSD`, an `edge-video` container encountered a Docker runtime condition where both `docker stop` and `docker kill` failed to receive an exit event. A host reboot restored normal Docker operation, after which the reset completed successfully. The script was not weakened to bypass that safety boundary.

## Architecture

The controller provides the management plane for nodes and their services:

~~~text
                     edge-controller
                           |
                    management plane
                           |
             +-------------+-------------+
             |             |             |
           Node          Node           Node
             |             |             |
         Services      Services      Services
             |             |             |
        capabilities   capabilities   capabilities
        observations   observations   observations
        configuration  configuration  configuration
        actions        actions        actions
~~~

A node is not limited to one service, and the controller must not assume a fixed service inventory.

The generic model is:

~~~text
Node
 └── Service
      ├── identity
      ├── version
      ├── status
      ├── capabilities
      ├── observation resources
      ├── endpoint
      └── configuration
~~~

The controller stores management metadata and state. The service remains responsible for implementing and interpreting its own service-specific behavior.

## Node and Service Model

Nodes have a persistent internal UUID and a logical node identifier.

Services are associated with nodes through the node UUID and are uniquely identified within a node by:

~~~text
(node_id, service_id)
~~~

This allows the same service to run on multiple nodes while allowing each node to host any number of services.

Service registration is idempotent. Re-registering an existing service refreshes its management metadata rather than requiring deletion and recreation.

A service registration can provide:

~~~text
service_id
name
version
endpoint
capabilities
observation_resources
~~~

Adding a service should not require a service-specific controller implementation or database model unless a demonstrated management-plane requirement cannot be represented by the generic model.

## Generic Service Observation

Services may declare multiple read-only observation resources.

A resource declaration contains:

~~~json
{
  "id": "health",
  "method": "GET",
  "path": "/health",
  "enabled": true,
  "description": "Service health"
}
~~~

The controller currently executes enabled GET resources.

For each resource, the controller:

1. Resolves the hosting node address.
2. Builds the service endpoint from the node address and exposed host port.
3. Performs the declared read-only request.
4. Records reachability and HTTP status independently.
5. Preserves the service response without assigning service-specific semantics.

A failure of one observation resource does not prevent the remaining resources from being observed.

Disabled resources and currently unsupported non-GET resources are reported as skipped by aggregate observation rather than executed.

The controller does not normalize, reinterpret, or make service-specific judgments from observation payloads.

## Observation API

The node-scoped observation APIs provide detailed management-plane observations:

~~~text
GET /api/v1/nodes/{node_id}/services/{service_id}/observe
GET /api/v1/nodes/{node_id}/services/{service_id}/observations/{resource_id}
GET /api/v1/nodes/{node_id}/services/{service_id}/observe-all
~~~

The fleet-scoped API observes all registered instances of a service:

~~~text
GET /api/v1/services/{service_id}/observe-all
~~~

Supporting metadata endpoints include:

~~~text
GET /api/v1/nodes/{node_id}/services/{service_id}/capabilities
GET /api/v1/nodes/{node_id}/services/{service_id}/observations
~~~

The node-scoped result is detailed. The fleet-scoped result is intentionally a compact generic summary so that fleet monitoring does not duplicate large service-specific payloads.

Observation results preserve information such as:

~~~text
service identity
service version
node identity
resource
endpoint
host-resolution behavior
reachability
HTTP status
content type
service response
observation timestamps
~~~

The aggregate timestamp for a multi-resource or fleet observation describes the controller's observation operation. It must not be interpreted as proof that distributed resources or nodes were sampled simultaneously.

## Generic Capabilities

Services may declare management-plane capabilities during registration.

Example:

~~~json
{
  "capabilities": {
    "status": true,
    "observe": true,
    "diagnostics": true,
    "configuration": false,
    "actions": false
  }
}
~~~

The controller stores capability declarations generically. The GUI and management APIs should use those declarations rather than hard-coded service-specific conditions.

Avoid patterns such as:

~~~text
if service == "edge-time"
~~~

inside generic controller or GUI logic.

A service-specific capability may be added when it represents a genuine generic management-plane concept. Its service-specific implementation and meaning remain owned by the service.

## Host Resolution and Service Endpoints

Inter-service HTTP uses the hosting node's network identity and exposed host port:

~~~text
<node-host>:<exposed-host-port>
~~~

Docker container names and Docker Compose service names must not be used as cross-service endpoints.

Example:

~~~text
http://pi4SSD.spoocannon.com:8095/health
~~~

not:

~~~text
http://edge-time:8095/health
~~~

The controller supports configurable node host resolution through:

~~~text
EDGE_NODE_HOST_MODE
EDGE_NODE_DOMAIN
~~~

Supported host modes are:

~~~text
short
domain
auto
~~~

- short uses the registered hostname.
- domain uses the configured domain-qualified hostname.
- auto attempts the short hostname and then the configured FQDN when a domain is available.

If a registered hostname is already an FQDN, the controller does not append the configured domain again.

Node identity remains independent of whichever network address is selected.

## API

### Nodes

~~~text
POST   /api/v1/nodes
GET    /api/v1/nodes
GET    /api/v1/nodes/{node_id}
DELETE /api/v1/nodes/{node_id}
~~~

### Services

~~~text
POST /api/v1/nodes/{node_id}/services
GET  /api/v1/nodes/{node_id}/services
~~~

### Service capabilities and observations

~~~text
GET /api/v1/nodes/{node_id}/services/{service_id}/capabilities
GET /api/v1/nodes/{node_id}/services/{service_id}/observations
GET /api/v1/nodes/{node_id}/services/{service_id}/observe
GET /api/v1/nodes/{node_id}/services/{service_id}/observations/{resource_id}
GET /api/v1/nodes/{node_id}/services/{service_id}/observe-all
GET /api/v1/services/{service_id}/observe-all
~~~

### Service endpoint

~~~text
GET /api/v1/nodes/{node_id}/services/{service_id}/endpoint
PUT /api/v1/nodes/{node_id}/services/{service_id}/endpoint
~~~

### Service configuration

~~~text
GET /api/v1/nodes/{node_id}/services/{service_id}/configuration
PUT /api/v1/nodes/{node_id}/services/{service_id}/configuration
~~~

### Service status

~~~text
GET /api/v1/nodes/{node_id}/services/{service_id}/status
PUT /api/v1/nodes/{node_id}/services/{service_id}/status
~~~

### Calibration

~~~text
POST /api/v1/nodes/{node_id}/services/{service_id}/calibration
GET  /api/v1/nodes/{node_id}/services/{service_id}/calibration/{calibration_id}
GET  /api/v1/nodes/{node_id}/calibration/pending
POST /api/v1/nodes/{node_id}/calibration/{calibration_id}/result
~~~

The calibration pending route also requires the service_id query parameter.

### Health

~~~text
GET /health
GET /api/v1/health
~~~

The API is intended to remain generic. New management APIs should preserve the node/service model and the controller's management-plane boundary.

## Calibration Boundary

Calibration is a controller-managed workflow, not controller-owned hardware logic.

The controller owns workflow state such as:

~~~text
job creation
assignment
status
result
error
~~~

The affected edge service owns:

~~~text
hardware measurement
calibration calculation
physical operation
~~~

This keeps the controller hardware-agnostic while allowing it to coordinate calibration jobs.

The current controller persists calibration jobs and exposes endpoints for job creation, pending-job retrieval, and result submission.

## Database

PostgreSQL is the controller's durable management-state store.

The current persistence model includes:

~~~text
nodes
services
service_endpoints
service_configurations
service_status
calibration_jobs
~~~

JSON fields are used for generic service capabilities, observation resources, service configuration, service status data, and calibration results where appropriate.

A new database technology should not be introduced without a demonstrated architectural requirement.

## GUI

The intended GUI model is dynamically discovered:

~~~text
Nodes
  |
  +-- Services
        |
        +-- Capabilities
        +-- Status
        +-- Observations
        +-- Configuration
        +-- Actions
~~~

The controller's data model and APIs are generic and must not assume a fixed service inventory.

The current service-detail template also contains service-specific presentation and calibration UI for existing services. That is an implementation detail of the current GUI, not a change to the generic controller data model. Future GUI work should move toward capability-driven and service-declared behavior rather than expanding hard-coded service conditions.

## Architectural Boundary

The controller is a **management and policy plane**.

It does not:

- Own original evidence produced by edge services
- Replace local edge-time in evidence capture
- Calculate physical sensor measurements
- Become a mandatory synchronous dependency for evidence capture
- Interpret service-specific observation payloads as generic platform facts

Evidence-producing services retain responsibility for local evidence preservation, temporal provenance, integrity, and service-specific capture behavior.

The common evidence model and temporal/provenance architecture are defined at the project level rather than duplicated here.

## Documentation

Project-wide architectural and engineering rules are maintained in:

~~~text
projectrules.md
~~~

The common evidence, temporal, provenance, integrity, observation, and reconstruction model is maintained in:

~~~text
evidencearchitecture.md
~~~

Current project work and development state are maintained in:

~~~text
sprintstatus.md
~~~

Service-specific implementation details belong in this repository and its source code. Current deployment/environment facts belong in the project's environment documentation rather than this README.