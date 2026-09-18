import os
import json
import socket
import urllib.error
import urllib.request

from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, ensure_schema, get_db
from .models import (
    Node,
    Service,
    ServiceEndpoint,
    ServiceConfiguration,
    ServiceStatus,
    CalibrationJob,
)
from .schemas import (
    NodeCreate,
    NodeResponse,
    ServiceCreate,
    ServiceResponse,
    ServiceEndpointCreate,
    ServiceEndpointResponse,
    ServiceConfigurationCreate,
    ServiceCapabilitiesResponse,
    ServiceObservationResourcesResponse,
    ServiceConfigurationResponse,
    CalibrationCreate,
    CalibrationResponse,
    ServiceStatusCreate,
    ServiceStatusResponse,
)


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

ensure_schema()


app = FastAPI(
    title="Edge Controller API",
    version="${SER_VER}",
)


templates = Jinja2Templates(
    directory="/app/app/templates"
)


app.mount(
    "/static",
    StaticFiles(directory="/app/app/static"),
    name="static",
)


# ---------------------------------------------------------------------------
# Controller network configuration
# ---------------------------------------------------------------------------

EDGE_NODE_HOST_MODE = os.environ.get(
    "EDGE_NODE_HOST_MODE",
    "auto",
).strip().lower()

EDGE_NODE_DOMAIN = os.environ.get(
    "EDGE_NODE_DOMAIN",
    "",
).strip().strip(".")


VALID_EDGE_NODE_HOST_MODES = {
    "short",
    "domain",
    "auto",
}


if EDGE_NODE_HOST_MODE not in VALID_EDGE_NODE_HOST_MODES:
    raise RuntimeError(
        "EDGE_NODE_HOST_MODE must be one of: "
        "short, domain, auto"
    )


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_endpoint_path(
    path: str | None,
) -> str:
    if not path:
        return "/"

    if not path.startswith("/"):
        return f"/{path}"

    return path


def normalize_node_hostname(
    hostname: str,
) -> str:
    return hostname.strip().rstrip(".")


def build_node_host_candidates(
    hostname: str,
) -> list[dict]:
    """
    Build the ordered network-address candidates for a node.

    Node identity remains independent of network addressing.

    Supported modes:

        short
            hostname only.

        domain
            hostname + EDGE_NODE_DOMAIN.

        auto
            short hostname first, then FQDN if a domain is configured.

    If the registered hostname is already an FQDN, it is not modified.
    """

    hostname = normalize_node_hostname(hostname)

    if not hostname:
        return []

    # If the node already registered an FQDN, don't append another domain.
    hostname_is_fqdn = "." in hostname

    short_candidate = {
        "mode": "short",
        "host": hostname,
    }

    if hostname_is_fqdn:
        fqdn_candidate = {
            "mode": "domain",
            "host": hostname,
        }
    elif EDGE_NODE_DOMAIN:
        fqdn_candidate = {
            "mode": "domain",
            "host": f"{hostname}.{EDGE_NODE_DOMAIN}",
        }
    else:
        fqdn_candidate = None

    if EDGE_NODE_HOST_MODE == "short":
        return [short_candidate]

    if EDGE_NODE_HOST_MODE == "domain":
        if fqdn_candidate is not None:
            return [fqdn_candidate]

        return [short_candidate]

    # auto
    candidates = [short_candidate]

    if fqdn_candidate is not None:
        fqdn_host = fqdn_candidate["host"]

        if fqdn_host != hostname:
            candidates.append(fqdn_candidate)

    return candidates

def build_observation_resource_url_for_host(
    host: str,
    endpoint: ServiceEndpoint,
    resource_path: str,
) -> str:
    path = normalize_endpoint_path(resource_path)

    return (
        f"{endpoint.scheme}://"
        f"{host}:"
        f"{endpoint.port}"
        f"{path}"
    )

def build_service_endpoint_url_for_host(
    host: str,
    endpoint: ServiceEndpoint,
) -> str:
    path = normalize_endpoint_path(endpoint.path)

    return (
        f"{endpoint.scheme}://"
        f"{host}:"
        f"{endpoint.port}"
        f"{path}"
    )


def build_service_endpoint_url(
    node: Node,
    endpoint: ServiceEndpoint,
) -> str:
    """
    Build the primary configured endpoint URL.

    This function does not perform network access.

    For auto mode, the first candidate is returned. Actual observation
    uses observe_registered_service(), which can fall back to additional
    candidates.
    """

    candidates = build_node_host_candidates(
        node.hostname,
    )

    if not candidates:
        raise ValueError(
            "Node hostname is empty"
        )

    return build_service_endpoint_url_for_host(
        candidates[0]["host"],
        endpoint,
    )


def get_node_or_404(
    db: Session,
    node_id: str,
) -> Node:
    node = (
        db.query(Node)
        .filter(
            Node.node_id == node_id
        )
        .first()
    )

    if not node:
        raise HTTPException(
            status_code=404,
            detail="Node not found",
        )

    return node


def get_service_or_404(
    db: Session,
    node: Node,
    service_id: str,
) -> Service:
    service = (
        db.query(Service)
        .filter(
            Service.node_id == node.id,
            Service.service_id == service_id,
        )
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    return service


def get_node_and_service(
    db: Session,
    node_id: str,
    service_id: str,
) -> tuple[Node, Service]:
    node = get_node_or_404(
        db,
        node_id,
    )

    service = get_service_or_404(
        db,
        node,
        service_id,
    )

    return node, service


def get_service_endpoint_or_404(
    db: Session,
    service: Service,
) -> ServiceEndpoint:
    endpoint = (
        db.query(ServiceEndpoint)
        .filter(
            ServiceEndpoint.service_id == service.id
        )
        .first()
    )

    if not endpoint:
        raise HTTPException(
            status_code=404,
            detail="Service endpoint not registered",
        )

    return endpoint

def get_observation_resource_or_404(
    service: Service,
    resource_id: str,
) -> dict:
    resources = service.observation_resources or []

    for resource in resources:
        if resource.get("id") == resource_id:
            return resource

    raise HTTPException(
        status_code=404,
        detail="Observation resource not found",
    )

def upsert_service_endpoint(
    db: Session,
    service: Service,
    endpoint_data: ServiceEndpointCreate | None,
):
    """
    Create or update generic endpoint metadata for a service.

    Endpoint metadata is management-plane information used by the
    controller for observation and future service actions.
    """

    if endpoint_data is None:
        return service.endpoint

    endpoint = (
        db.query(ServiceEndpoint)
        .filter(
            ServiceEndpoint.service_id == service.id
        )
        .first()
    )

    if endpoint is None:
        endpoint = ServiceEndpoint(
            service_id=service.id,
            scheme=endpoint_data.scheme,
            port=endpoint_data.port,
            path=endpoint_data.path,
        )

        db.add(endpoint)

    else:
        endpoint.scheme = endpoint_data.scheme
        endpoint.port = endpoint_data.port
        endpoint.path = endpoint_data.path

    return endpoint

def normalize_observation_resources(
    resources,
) -> list[dict]:
    """
    Normalize generic service observation declarations.

    The controller stores declarations as service metadata. It does not
    interpret service-specific resource IDs or response payloads.
    """

    normalized = []

    for resource in resources or []:

        item = resource.model_dump(
            exclude_none=True,
        )

        method = str(
            item.get("method", "GET")
        ).upper()

        path = item.get(
            "path",
            "/",
        )

        if not path.startswith("/"):
            path = f"/{path}"

        item["method"] = method
        item["path"] = path
        item["enabled"] = bool(
            item.get("enabled", True)
        )

        normalized.append(item)

    return normalized
# ---------------------------------------------------------------------------
# Generic service observation
# ---------------------------------------------------------------------------

def observe_registered_service(
    node: Node,
    service: Service,
) -> dict:
    """
    Query a registered service through its host-addressed endpoint.

    The controller intentionally uses the hosting node's network address
    and exposed service port. Docker container/service names are never used.

    Host selection is controlled by:

        EDGE_NODE_HOST_MODE
        EDGE_NODE_DOMAIN

    In auto mode, the short hostname is attempted first, followed by the
    configured FQDN when available.
    """

    endpoint = service.endpoint

    observed_at = utc_now_iso()

    base_result = {
        "service_id": service.service_id,
        "service_name": service.name,
        "version": service.version,
        "node_id": node.node_id,
        "node_hostname": node.hostname,
        "observed_at": observed_at,
    }

    if endpoint is None:
        return {
            **base_result,
            "reachable": False,
            "error": "Service endpoint is not registered",
        }

    candidates = build_node_host_candidates(
        node.hostname,
    )

    if not candidates:
        return {
            **base_result,
            "reachable": False,
            "error": "Node hostname is empty",
        }

    attempts = []

    for candidate in candidates:
        host = candidate["host"]

        url = build_service_endpoint_url_for_host(
            host,
            endpoint,
        )

        attempt = {
            "mode": candidate["mode"],
            "host": host,
            "url": url,
            "reachable": False,
        }

        result = {
            **base_result,
            "endpoint": {
                "scheme": endpoint.scheme,
                "host": host,
                "port": endpoint.port,
                "path": normalize_endpoint_path(
                    endpoint.path
                ),
                "url": url,
            },
            "host_resolution": {
                "mode": EDGE_NODE_HOST_MODE,
                "domain": EDGE_NODE_DOMAIN or None,
                "selected": None,
                "attempts": attempts,
            },
            "reachable": False,
        }

        try:
            request = urllib.request.Request(
                url,
                method="GET",
                headers={
                    "Accept": "application/json",
                    "User-Agent": "edge-controller-observer",
                },
            )

            with urllib.request.urlopen(
                request,
                timeout=5,
            ) as response:

                raw = response.read()

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    )
                    or ""
                ).lower()

                payload = None

                if raw:
                    decoded = raw.decode(
                        "utf-8",
                        errors="replace",
                    )

                    if (
                        "application/json" in content_type
                        or decoded.lstrip().startswith("{")
                        or decoded.lstrip().startswith("[")
                    ):
                        try:
                            payload = json.loads(
                                decoded
                            )
                        except json.JSONDecodeError:
                            payload = {
                                "raw": decoded,
                            }

                    else:
                        payload = {
                            "raw": decoded,
                        }

                attempt.update(
                    {
                        "reachable": True,
                        "http_status": response.status,
                    }
                )

                attempts.append(attempt)

                result["host_resolution"][
                    "selected"
                ] = {
                    "mode": candidate["mode"],
                    "host": host,
                }

                result.update(
                    {
                        "reachable": True,
                        "http_status": response.status,
                        "content_type": content_type,
                        "response": payload,
                    }
                )

                return result

        except urllib.error.HTTPError as exc:
            attempt.update(
                {
                    "http_status": exc.code,
                    "error": f"HTTP error {exc.code}",
                }
            )

            attempts.append(attempt)

            # An HTTP response proves that the host and service are
            # reachable, even if the service returned an error status.
            result["host_resolution"][
                "selected"
            ] = {
                "mode": candidate["mode"],
                "host": host,
            }

            result.update(
                {
                    "reachable": True,
                    "http_status": exc.code,
                    "content_type": (
                        exc.headers.get(
                            "Content-Type",
                            "",
                        )
                        or ""
                    ).lower(),
                    "error": f"HTTP error {exc.code}",
                }
            )

            return result

        except urllib.error.URLError as exc:
            reason = exc.reason

            if isinstance(
                reason,
                socket.timeout,
            ):
                error = "Connection timed out"
            else:
                error = str(reason)

            attempt["error"] = error
            attempts.append(attempt)

        except socket.timeout:
            attempt["error"] = "Connection timed out"
            attempts.append(attempt)

        except TimeoutError:
            attempt["error"] = "Connection timed out"
            attempts.append(attempt)

        except ConnectionRefusedError:
            attempt["error"] = "Connection refused"
            attempts.append(attempt)

        except OSError as exc:
            attempt["error"] = str(exc)
            attempts.append(attempt)

        except Exception as exc:
            attempt["error"] = str(exc)
            attempts.append(attempt)

    # All candidates failed.
    last_error = (
        attempts[-1].get("error")
        if attempts
        else "No network address candidates available"
    )

    final_candidates = []

    for attempt in attempts:
        final_candidates.append(
            {
                "mode": attempt.get("mode"),
                "host": attempt.get("host"),
                "url": attempt.get("url"),
                "reachable": attempt.get(
                    "reachable",
                    False,
                ),
                "http_status": attempt.get(
                    "http_status"
                ),
                "error": attempt.get(
                    "error"
                ),
            }
        )

    return {
        **base_result,
        "endpoint": {
            "scheme": endpoint.scheme,
            "host": candidates[0]["host"],
            "port": endpoint.port,
            "path": normalize_endpoint_path(
                endpoint.path
            ),
            "url": build_service_endpoint_url_for_host(
                candidates[0]["host"],
                endpoint,
            ),
        },
        "host_resolution": {
            "mode": EDGE_NODE_HOST_MODE,
            "domain": EDGE_NODE_DOMAIN or None,
            "selected": None,
            "attempts": final_candidates,
        },
        "reachable": False,
        "error": last_error,
    }

def observe_registered_resource(
    node: Node,
    service: Service,
    resource: dict,
) -> dict:
    """
    Execute one declared read-only observation resource.

    Resource execution is intentionally generic. The controller does not
    interpret service-specific resource IDs or response payloads.

    Only GET resources are executable at this stage. Future write/action
    semantics will be introduced separately.
    """

    endpoint = service.endpoint
    observed_at = utc_now_iso()

    base_result = {
        "service_id": service.service_id,
        "service_name": service.name,
        "version": service.version,
        "node_id": node.node_id,
        "node_hostname": node.hostname,
        "resource": {
            "id": resource.get("id"),
            "method": str(
                resource.get("method", "GET")
            ).upper(),
            "path": normalize_endpoint_path(
                resource.get("path", "/")
            ),
            "enabled": bool(
                resource.get("enabled", True)
            ),
            "description": resource.get("description"),
        },
        "observed_at": observed_at,
    }

    if endpoint is None:
        return {
            **base_result,
            "reachable": False,
            "error": "Service endpoint is not registered",
        }

    method = str(
        resource.get("method", "GET")
    ).upper()

    if method != "GET":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only GET observation resources are currently "
                "executable"
            ),
        )

    if not bool(
        resource.get("enabled", True)
    ):
        raise HTTPException(
            status_code=409,
            detail="Observation resource is disabled",
        )

    resource_path = normalize_endpoint_path(
        resource.get("path", "/")
    )

    candidates = build_node_host_candidates(
        node.hostname,
    )

    if not candidates:
        return {
            **base_result,
            "reachable": False,
            "error": "Node hostname is empty",
        }

    attempts = []

    for candidate in candidates:
        host = candidate["host"]

        url = build_observation_resource_url_for_host(
            host,
            endpoint,
            resource_path,
        )

        attempt = {
            "mode": candidate["mode"],
            "host": host,
            "url": url,
            "reachable": False,
        }

        result = {
            **base_result,
            "endpoint": {
                "scheme": endpoint.scheme,
                "host": host,
                "port": endpoint.port,
                "url": (
                    f"{endpoint.scheme}://"
                    f"{host}:"
                    f"{endpoint.port}"
                ),
            },
            "host_resolution": {
                "mode": EDGE_NODE_HOST_MODE,
                "domain": EDGE_NODE_DOMAIN or None,
                "selected": None,
                "attempts": attempts,
            },
            "reachable": False,
        }

        try:
            request = urllib.request.Request(
                url,
                method="GET",
                headers={
                    "Accept": "application/json",
                    "User-Agent": (
                        "edge-controller-observer"
                    ),
                },
            )

            with urllib.request.urlopen(
                request,
                timeout=5,
            ) as response:

                raw = response.read()

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    )
                    or ""
                ).lower()

                payload = None

                if raw:
                    decoded = raw.decode(
                        "utf-8",
                        errors="replace",
                    )

                    if (
                        "application/json"
                        in content_type
                        or decoded.lstrip().startswith("{")
                        or decoded.lstrip().startswith("[")
                    ):
                        try:
                            payload = json.loads(
                                decoded
                            )
                        except json.JSONDecodeError:
                            payload = {
                                "raw": decoded,
                            }
                    else:
                        payload = {
                            "raw": decoded,
                        }

                attempt.update(
                    {
                        "reachable": True,
                        "http_status": response.status,
                    }
                )

                attempts.append(attempt)

                result["host_resolution"][
                    "selected"
                ] = {
                    "mode": candidate["mode"],
                    "host": host,
                }

                result.update(
                    {
                        "reachable": True,
                        "http_status": response.status,
                        "content_type": content_type,
                        "response": payload,
                    }
                )

                return result

        except urllib.error.HTTPError as exc:
            attempt.update(
                {
                    "reachable": True,
                    "http_status": exc.code,
                    "error": (
                        f"HTTP error {exc.code}"
                    ),
                }
            )

            attempts.append(attempt)

            result["host_resolution"][
                "selected"
            ] = {
                "mode": candidate["mode"],
                "host": host,
            }

            result.update(
                {
                    "reachable": True,
                    "http_status": exc.code,
                    "content_type": (
                        exc.headers.get(
                            "Content-Type",
                            "",
                        )
                        or ""
                    ).lower(),
                    "error": (
                        f"HTTP error {exc.code}"
                    ),
                }
            )

            return result

        except urllib.error.URLError as exc:
            reason = exc.reason

            if isinstance(
                reason,
                socket.timeout,
            ):
                error = "Connection timed out"
            else:
                error = str(reason)

            attempt["error"] = error
            attempts.append(attempt)

        except socket.timeout:
            attempt["error"] = (
                "Connection timed out"
            )
            attempts.append(attempt)

        except TimeoutError:
            attempt["error"] = (
                "Connection timed out"
            )
            attempts.append(attempt)

        except ConnectionRefusedError:
            attempt["error"] = (
                "Connection refused"
            )
            attempts.append(attempt)

        except OSError as exc:
            attempt["error"] = str(exc)
            attempts.append(attempt)

        except Exception as exc:
            attempt["error"] = str(exc)
            attempts.append(attempt)

    last_error = (
        attempts[-1].get("error")
        if attempts
        else "No network address candidates available"
    )

    final_candidates = []

    for attempt in attempts:
        final_candidates.append(
            {
                "mode": attempt.get("mode"),
                "host": attempt.get("host"),
                "url": attempt.get("url"),
                "reachable": attempt.get(
                    "reachable",
                    False,
                ),
                "http_status": attempt.get(
                    "http_status"
                ),
                "error": attempt.get(
                    "error"
                ),
            }
        )

    return {
        **base_result,
        "endpoint": {
            "scheme": endpoint.scheme,
            "host": candidates[0]["host"],
            "port": endpoint.port,
            "url": (
                f"{endpoint.scheme}://"
                f"{candidates[0]['host']}:"
                f"{endpoint.port}"
            ),
        },
        "host_resolution": {
            "mode": EDGE_NODE_HOST_MODE,
            "domain": EDGE_NODE_DOMAIN or None,
            "selected": None,
            "attempts": final_candidates,
        },
        "reachable": False,
        "error": last_error,
    }

def observe_registered_resources(
    node: Node,
    service: Service,
) -> dict:
    """
    Execute all enabled, declared GET observation resources for a service.

    The controller remains service-agnostic. Each resource is executed
    independently through observe_registered_resource().

    A failure in one resource does not prevent the remaining resources
    from being observed.

    Each resource retains its own observed_at timestamp. The aggregate
    observed_at value represents the start of the aggregate request and
    is not a shared sample timestamp.
    """

    aggregate_observed_at = utc_now_iso()

    resources = service.observation_resources or []

    results = {}

    for resource in resources:
        resource_id = resource.get("id")

        if not resource_id:
            continue

        method = str(
            resource.get("method", "GET")
        ).upper()

        enabled = bool(
            resource.get("enabled", True)
        )

        if not enabled:
            results[resource_id] = {
                "resource": {
                    "id": resource_id,
                    "method": method,
                    "path": normalize_endpoint_path(
                        resource.get("path", "/")
                    ),
                    "enabled": False,
                    "description": resource.get(
                        "description"
                    ),
                },
                "observed_at": utc_now_iso(),
                "skipped": True,
                "reason": "Observation resource is disabled",
            }

            continue

        if method != "GET":
            results[resource_id] = {
                "resource": {
                    "id": resource_id,
                    "method": method,
                    "path": normalize_endpoint_path(
                        resource.get("path", "/")
                    ),
                    "enabled": True,
                    "description": resource.get(
                        "description"
                    ),
                },
                "observed_at": utc_now_iso(),
                "skipped": True,
                "reason": (
                    "Only GET observation resources are "
                    "currently executable"
                ),
            }

            continue

        try:
            results[resource_id] = (
                observe_registered_resource(
                    node,
                    service,
                    resource,
                )
            )

        except Exception as exc:
            results[resource_id] = {
                "resource": {
                    "id": resource_id,
                    "method": method,
                    "path": normalize_endpoint_path(
                        resource.get("path", "/")
                    ),
                    "enabled": enabled,
                    "description": resource.get(
                        "description"
                    ),
                },
                "observed_at": utc_now_iso(),
                "reachable": False,
                "error": str(exc),
            }

    return {
        "service_id": service.service_id,
        "service_name": service.name,
        "version": service.version,
        "node_id": node.node_id,
        "node_hostname": node.hostname,
        "observed_at": aggregate_observed_at,
        "resource_count": len(results),
        "resources": results,
    }
def summarize_observation_result(
    observation: dict,
) -> dict:
    """
    Convert a detailed node observation into a compact fleet summary.

    The controller remains service-agnostic. It reports only generic
    observation metadata and HTTP reachability/status information.

    Service-specific response payloads are intentionally omitted.
    """

    resources = observation.get(
        "resources",
        {},
    )

    resource_statuses = {}

    for resource_id, result in resources.items():
        if result.get("skipped"):
            resource_statuses[resource_id] = None
            continue

        resource_statuses[resource_id] = result.get(
            "http_status"
        )

    return {
        "node_hostname": observation.get(
            "node_hostname"
        ),
        "version": observation.get(
            "version",
            "unknown",
        ),
        "reachable": any(
            result.get("reachable") is True
            for result in resources.values()
            if isinstance(result, dict)
        ),
        "resource_count": observation.get(
            "resource_count",
            len(resources),
        ),
        "resources": resource_statuses,
        **(
            {
                "error": observation["error"],
            }
            if observation.get("error")
            else {}
        ),
    }


def observe_service_across_nodes(
    db: Session,
    service_id: str,
) -> dict:
    """
    Execute the declared read-only observation resources for a service
    across every registered node that hosts that service.

    The fleet-scoped endpoint intentionally returns a compact summary.
    Detailed resource observations remain available through the
    node-scoped observe-all endpoint.

    The controller remains service-agnostic. It does not interpret
    service-specific response payloads or calculate service-specific
    health/quality semantics.

    Each node is observed independently. A failure on one node does
    not prevent observations from the remaining nodes.

    The aggregate observed_at value represents the start of the
    cross-node request and is not a shared sample timestamp.
    """

    aggregate_observed_at = utc_now_iso()

    services = (
        db.query(Service)
        .join(
            Node,
            Service.node_id == Node.id,
        )
        .filter(
            Service.service_id == service_id,
        )
        .order_by(
            Node.hostname,
        )
        .all()
    )

    results = {}

    for service in services:
        node = service.node

        try:
            observation = (
                observe_registered_resources(
                    node,
                    service,
                )
            )

            results[node.node_id] = (
                summarize_observation_result(
                    observation,
                )
            )

        except Exception as exc:
            results[node.node_id] = {
                "node_hostname": node.hostname,
                "version": service.version or "unknown",
                "reachable": False,
                "resource_count": 0,
                "resources": {},
                "error": str(exc),
            }

    return {
        "service_id": service_id,
        "observed_at": aggregate_observed_at,
        "node_count": len(results),
        "nodes": results,
    }

# ---------------------------------------------------------------------------
# Web pages
# ---------------------------------------------------------------------------

@app.get("/")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    nodes = (
        db.query(Node)
        .order_by(Node.hostname)
        .all()
    )

    service_count = sum(
        len(node.services)
        for node in nodes
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "nodes": nodes,
            "service_count": service_count,
        },
    )


@app.get("/nodes")
def nodes_page(
    request: Request,
    db: Session = Depends(get_db),
):
    nodes = (
        db.query(Node)
        .order_by(Node.hostname)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="nodes.html",
        context={
            "nodes": nodes,
        },
    )


@app.get("/nodes/{node_id}")
def node_page(
    request: Request,
    node_id: str,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    return templates.TemplateResponse(
        request=request,
        name="node.html",
        context={
            "node": node,
        },
    )


@app.get(
    "/nodes/{node_id}/services/{service_id}"
)
def service_page(
    request: Request,
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    service_status = (
        db.query(ServiceStatus)
        .filter(
            ServiceStatus.service_id == service.id
        )
        .first()
    )

    return templates.TemplateResponse(
        request=request,
        name="service.html",
        context={
            "node": node,
            "service": service,
            "service_status": service_status,
        },
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/api/v1/health")
def api_health():
    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        database_status = "ok"

    except SQLAlchemyError:
        database_status = "error"

    status = (
        "ok"
        if database_status == "ok"
        else "degraded"
    )

    return {
        "status": status,
        "database": database_status,
    }


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

@app.post(
    "/api/v1/nodes",
    response_model=NodeResponse,
)
def create_node(
    node: NodeCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Node)
        .filter(
            Node.node_id == node.node_id
        )
        .first()
    )

    if existing:
        existing.hostname = node.hostname
        existing.platform = node.platform
        existing.status = "online"

        db.commit()
        db.refresh(existing)

        return existing

    db_node = Node(
        node_id=node.node_id,
        hostname=node.hostname,
        platform=node.platform,
        status="online",
    )

    db.add(db_node)
    db.commit()
    db.refresh(db_node)

    return db_node


@app.get(
    "/api/v1/nodes",
    response_model=list[NodeResponse],
)
def list_nodes(
    db: Session = Depends(get_db),
):
    return (
        db.query(Node)
        .order_by(Node.hostname)
        .all()
    )


@app.get(
    "/api/v1/nodes/{node_id}",
    response_model=NodeResponse,
)
def get_node(
    node_id: str,
    db: Session = Depends(get_db),
):
    return get_node_or_404(
        db,
        node_id,
    )


@app.delete(
    "/api/v1/nodes/{node_id}",
)
def delete_node(
    node_id: str,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    try:
        service_ids = [
            service.id
            for service in node.services
        ]

        if service_ids:
            db.query(ServiceStatus).filter(
                ServiceStatus.service_id.in_(
                    service_ids
                )
            ).delete(
                synchronize_session=False
            )

            db.query(ServiceEndpoint).filter(
                ServiceEndpoint.service_id.in_(
                    service_ids
                )
            ).delete(
                synchronize_session=False
            )

            db.query(ServiceConfiguration).filter(
                ServiceConfiguration.service_id.in_(
                    service_ids
                )
            ).delete(
                synchronize_session=False
            )

            db.query(Service).filter(
                Service.id.in_(
                    service_ids
                )
            ).delete(
                synchronize_session=False
            )

        db.query(CalibrationJob).filter(
            CalibrationJob.node_id == node.id
        ).delete(
            synchronize_session=False
        )

        db.delete(node)
        db.commit()

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to remove node",
        )

    return {
        "status": "removed",
        "node_id": node_id,
    }


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

@app.post(
    "/api/v1/nodes/{node_id}/services",
    response_model=ServiceResponse,
)
def create_service(
    node_id: str,
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    capabilities = dict(
        service.capabilities or {}
    )

    observation_resources = (
        normalize_observation_resources(
            service.observation_resources
        )
    )

    existing = (
        db.query(Service)
        .filter(
            Service.node_id == node.id,
            Service.service_id == service.service_id,
        )
        .first()
    )

    if existing:

        existing.name = service.name
        existing.version = service.version
        existing.status = "online"
        existing.capabilities = capabilities
        existing.observation_resources = (
            observation_resources
        )

        upsert_service_endpoint(
            db,
            existing,
            service.endpoint,
        )

        configuration = (
            db.query(ServiceConfiguration)
            .filter(
                ServiceConfiguration.service_id
                == existing.id
            )
            .first()
        )

        if not configuration:
            configuration = ServiceConfiguration(
                service_id=existing.id,
                configuration={},
            )

            db.add(configuration)

        db.commit()
        db.refresh(existing)

        return existing

    db_service = Service(
        service_id=service.service_id,
        node_id=node.id,
        name=service.name,
        version=service.version,
        status="online",
        capabilities=capabilities,
        observation_resources=(
            observation_resources
        ),
    )

    db.add(db_service)
    db.flush()

    upsert_service_endpoint(
        db,
        db_service,
        service.endpoint,
    )

    configuration = ServiceConfiguration(
        service_id=db_service.id,
        configuration={},
    )

    db.add(configuration)

    db.commit()
    db.refresh(db_service)

    return db_service

@app.get(
    "/api/v1/nodes/{node_id}/services",
    response_model=list[ServiceResponse],
)
def list_services(
    node_id: str,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    return (
        db.query(Service)
        .filter(
            Service.node_id == node.id
        )
        .order_by(Service.name)
        .all()
    )

@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/capabilities",
    response_model=ServiceCapabilitiesResponse,
)
def get_service_capabilities(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    return {
        "service_id": service.service_id,
        "node_id": node.node_id,
        "capabilities": (
            service.capabilities or {}
        ),
        "updated_at": service.updated_at,
    }


@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/observations",
    response_model=ServiceObservationResourcesResponse,
)
def get_service_observation_resources(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    return {
        "service_id": service.service_id,
        "node_id": node.node_id,
        "resources": (
            service.observation_resources or []
        ),
        "updated_at": service.updated_at,
    }

@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/observe",
)
def observe_service(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    """
    Generic read-only observation endpoint.

    Example:

        GET /api/v1/nodes/pi4SSD/services/edge-time/observe
    """

    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    return observe_registered_service(
        node,
        service,
    )

@app.get(
    "/api/v1/nodes/{node_id}/services/"
    "{service_id}/observations/{resource_id}",
)
def observe_service_resource(
    node_id: str,
    service_id: str,
    resource_id: str,
    db: Session = Depends(get_db),
):
    """
    Execute one declared read-only observation resource.

    Example:

        GET /api/v1/nodes/pi4SSD/services/edge-time/observations/sources
    """

    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    resource = get_observation_resource_or_404(
        service,
        resource_id,
    )

    return observe_registered_resource(
        node,
        service,
        resource,
    )

@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/observe-all",
)
def observe_all_service_resources(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    """
    Execute all declared read-only observation resources for a service.

    Each resource is observed independently. A failure in one resource
    does not prevent the remaining resources from being observed.

    Example:

        GET /api/v1/nodes/pi4SSD/services/edge-time/observe-all
    """

    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    return observe_registered_resources(
        node,
        service,
    )

@app.get(
    "/api/v1/services/{service_id}/observe-all",
)
def observe_service_across_all_nodes(
    service_id: str,
    db: Session = Depends(get_db),
):
    """
    Execute all declared read-only observation resources for a service
    across every registered node hosting that service.

    The controller performs aggregation only. It does not interpret
    service-specific response payloads.
    """

    return observe_service_across_nodes(
        db,
        service_id,
    )
# ---------------------------------------------------------------------------
# Service endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/endpoint",
)
def get_service_endpoint(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    endpoint = get_service_endpoint_or_404(
        db,
        service,
    )

    path = normalize_endpoint_path(
        endpoint.path
    )

    url = build_service_endpoint_url(
        node,
        endpoint,
    )

    return {
        "service_id": service.service_id,
        "node_id": node.node_id,
        "host": node.hostname,
        "scheme": endpoint.scheme,
        "port": endpoint.port,
        "path": path,
        "url": url,
        "host_resolution": {
            "mode": EDGE_NODE_HOST_MODE,
            "domain": EDGE_NODE_DOMAIN or None,
            "candidates": build_node_host_candidates(
                node.hostname
            ),
        },
    }


@app.put(
    "/api/v1/nodes/{node_id}/services/{service_id}/endpoint",
    response_model=ServiceEndpointResponse,
)
def update_service_endpoint(
    node_id: str,
    service_id: str,
    payload: ServiceEndpointCreate,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    endpoint = (
        db.query(ServiceEndpoint)
        .filter(
            ServiceEndpoint.service_id == service.id
        )
        .first()
    )

    if not endpoint:
        endpoint = ServiceEndpoint(
            service_id=service.id,
            scheme=payload.scheme,
            port=payload.port,
            path=payload.path,
        )

        db.add(endpoint)

    else:
        endpoint.scheme = payload.scheme
        endpoint.port = payload.port
        endpoint.path = payload.path

    db.commit()
    db.refresh(endpoint)

    return endpoint


# ---------------------------------------------------------------------------
# Service configuration
# ---------------------------------------------------------------------------

@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/configuration",
    response_model=ServiceConfigurationResponse,
)
def get_service_configuration(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    configuration = (
        db.query(ServiceConfiguration)
        .filter(
            ServiceConfiguration.service_id
            == service.id
        )
        .first()
    )

    if not configuration:
        configuration = ServiceConfiguration(
            service_id=service.id,
            configuration={},
        )

        db.add(configuration)
        db.commit()
        db.refresh(configuration)

    return configuration


@app.put(
    "/api/v1/nodes/{node_id}/services/{service_id}/configuration",
    response_model=ServiceConfigurationResponse,
)
def update_service_configuration(
    node_id: str,
    service_id: str,
    payload: ServiceConfigurationCreate,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    configuration = (
        db.query(ServiceConfiguration)
        .filter(
            ServiceConfiguration.service_id
            == service.id
        )
        .first()
    )

    if not configuration:
        configuration = ServiceConfiguration(
            service_id=service.id,
            configuration=payload.configuration,
        )

        db.add(configuration)

    else:
        configuration.configuration = (
            payload.configuration
        )

    db.commit()
    db.refresh(configuration)

    return configuration


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

@app.post(
    "/api/v1/nodes/{node_id}/services/{service_id}/calibration",
    response_model=CalibrationResponse,
)
def create_calibration(
    node_id: str,
    service_id: str,
    calibration: CalibrationCreate,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    if calibration.duration_seconds < 1:
        raise HTTPException(
            status_code=400,
            detail="duration_seconds must be at least 1",
        )

    if calibration.duration_seconds > 60:
        raise HTTPException(
            status_code=400,
            detail="duration_seconds cannot exceed 60",
        )

    job = CalibrationJob(
        node_id=node.id,
        service_id=service_id,
        status="pending",
        duration_seconds=calibration.duration_seconds,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/calibration/{calibration_id}",
    response_model=CalibrationResponse,
)
def get_calibration(
    node_id: str,
    service_id: str,
    calibration_id: UUID,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    job = (
        db.query(CalibrationJob)
        .filter(
            CalibrationJob.id == calibration_id,
            CalibrationJob.node_id == node.id,
            CalibrationJob.service_id == service_id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Calibration job not found",
        )

    return job


@app.get(
    "/api/v1/nodes/{node_id}/calibration/pending",
)
def get_pending_calibration(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    service = get_service_or_404(
        db,
        node,
        service_id,
    )

    job = (
        db.query(CalibrationJob)
        .filter(
            CalibrationJob.node_id == node.id,
            CalibrationJob.service_id == service_id,
            CalibrationJob.status == "pending",
        )
        .order_by(CalibrationJob.created_at)
        .first()
    )

    if not job:
        return None

    job.status = "running"

    db.commit()
    db.refresh(job)

    return {
        "id": str(job.id),
        "service_id": job.service_id,
        "duration_seconds": job.duration_seconds,
    }


@app.post(
    "/api/v1/nodes/{node_id}/calibration/{calibration_id}/result",
)
def complete_calibration(
    node_id: str,
    calibration_id: UUID,
    payload: dict,
    db: Session = Depends(get_db),
):
    node = get_node_or_404(
        db,
        node_id,
    )

    job = (
        db.query(CalibrationJob)
        .filter(
            CalibrationJob.id == calibration_id,
            CalibrationJob.node_id == node.id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Calibration job not found",
        )

    job.status = payload.get(
        "status",
        "complete",
    )

    job.result = json.dumps(
        payload.get("result")
    )

    job.error = payload.get("error")

    db.commit()
    db.refresh(job)

    return {
        "status": job.status,
    }


# ---------------------------------------------------------------------------
# Service status
# ---------------------------------------------------------------------------

@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/status",
    response_model=ServiceStatusResponse,
)
def get_service_status(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    status = (
        db.query(ServiceStatus)
        .filter(
            ServiceStatus.service_id == service.id
        )
        .first()
    )

    if not status:
        raise HTTPException(
            status_code=404,
            detail="Service status not available",
        )

    return status


@app.put(
    "/api/v1/nodes/{node_id}/services/{service_id}/status",
    response_model=ServiceStatusResponse,
)
def update_service_status(
    node_id: str,
    service_id: str,
    payload: ServiceStatusCreate,
    db: Session = Depends(get_db),
):
    node, service = get_node_and_service(
        db,
        node_id,
        service_id,
    )

    service_status = (
        db.query(ServiceStatus)
        .filter(
            ServiceStatus.service_id == service.id
        )
        .first()
    )

    if not service_status:
        service_status = ServiceStatus(
            service_id=service.id,
            status=payload.status,
            data=payload.data,
        )

        db.add(service_status)

    else:
        service_status.status = payload.status
        service_status.data = payload.data

    db.commit()
    db.refresh(service_status)

    return service_status