import os
import json

from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, get_db
from .models import (
    Node,
    Service,
    ServiceConfiguration,
    CalibrationJob,
)
from .schemas import (
    NodeCreate,
    NodeResponse,
    ServiceCreate,
    ServiceResponse,
    ServiceConfigurationCreate,
    ServiceConfigurationResponse,
    CalibrationCreate,
    CalibrationResponse,
)


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Edge Controller API",
    version="0.1.0",
)

templates = Jinja2Templates(
    directory="/app/app/templates"
)

app.mount(
    "/static",
    StaticFiles(directory="/app/app/static"),
    name="static",
)
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

    return templates.TemplateResponse(
        request=request,
        name="service.html",
        context={
            "node": node,
            "service": service,
        },
    )

@app.get("/health")
def health():
    return {
        "status": "ok"
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
        existing.name = service.name
        existing.version = service.version
        existing.status = "online"

        configuration = (
            db.query(ServiceConfiguration)
            .filter(
                ServiceConfiguration.service_id == existing.id
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


@app.post(
    "/api/v1/nodes/{node_id}/services",
    response_model=ServiceResponse,
)
def create_service(
    node_id: str,
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
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

        configuration = (
            db.query(ServiceConfiguration)
            .filter(
                ServiceConfiguration.service_id == existing.id
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
    )

    db.add(db_service)
    db.flush()

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

    return (
        db.query(Service)
        .filter(
            Service.node_id == node.id
        )
        .order_by(Service.name)
        .all()
    )


@app.get(
    "/api/v1/nodes/{node_id}/services/{service_id}/configuration",
    response_model=ServiceConfigurationResponse,
)
def get_service_configuration(
    node_id: str,
    service_id: str,
    db: Session = Depends(get_db),
):
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

    configuration = (
        db.query(ServiceConfiguration)
        .filter(
            ServiceConfiguration.service_id == service.id
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

    configuration = (
        db.query(ServiceConfiguration)
        .filter(
            ServiceConfiguration.service_id == service.id
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
        configuration.configuration = payload.configuration

    db.commit()
    db.refresh(configuration)

    return configuration

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
        "complete"
    )

    job.result = json.dumps(
        payload.get("result")
    )

    job.error = payload.get("error")

    db.commit()
    db.refresh(job)

    return {
        "status": job.status
    }

