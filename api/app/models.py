from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    node_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    hostname: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    platform: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="online",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    services: Mapped[list["Service"]] = relationship(
        back_populates="node",
        cascade="all, delete-orphan",
    )


class Service(Base):
    __tablename__ = "services"

    __table_args__ = (
        UniqueConstraint(
            "node_id",
            "service_id",
            name="uq_service_node_service",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    service_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    node_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "nodes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="online",
    )

    capabilities: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    observation_resources: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    node: Mapped["Node"] = relationship(
        back_populates="services",
    )

    endpoint: Mapped["ServiceEndpoint | None"] = relationship(
        back_populates="service",
        uselist=False,
        cascade="all, delete-orphan",
    )

    configuration: Mapped["ServiceConfiguration | None"] = relationship(
        back_populates="service",
        uselist=False,
        cascade="all, delete-orphan",
    )

    service_status: Mapped["ServiceStatus | None"] = relationship(
        back_populates="service",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ServiceEndpoint(Base):
    __tablename__ = "service_endpoints"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    service_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    scheme: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="http",
    )

    port: Mapped[int] = mapped_column(
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="/",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    service: Mapped["Service"] = relationship(
        back_populates="endpoint",
    )


class ServiceConfiguration(Base):
    __tablename__ = "service_configurations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    service_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    configuration: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    service: Mapped["Service"] = relationship(
        back_populates="configuration",
    )


class ServiceStatus(Base):
    __tablename__ = "service_status"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    service_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    service: Mapped["Service"] = relationship(
        back_populates="service_status",
    )


class CalibrationJob(Base):
    __tablename__ = "calibration_jobs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    node_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "nodes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    service_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending",
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    result: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )