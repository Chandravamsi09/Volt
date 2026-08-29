"""
Database Models for Experiments, Runs, Models, Deployments and Drift
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Experiment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """ML Experiment group container."""

    __tablename__ = "experiments"

    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")


class Run(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual training or evaluation execution run."""

    __tablename__ = "runs"

    experiment_id = Column(String(36), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(50), default="RUNNING", nullable=False)  # RUNNING, COMPLETED, FAILED, KILLED
    parameters = Column(JSON, default=dict, nullable=False)
    metrics = Column(JSON, default=dict, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)

    experiment = relationship("Experiment", back_populates="runs")
    artifacts = relationship("ModelArtifact", back_populates="run", cascade="all, delete-orphan")


class ModelArtifact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registered machine learning model version."""

    __tablename__ = "model_artifacts"

    name = Column(String(100), index=True, nullable=False)
    version = Column(String(50), nullable=False)  # e.g. "1.0.0" or "v1"
    run_id = Column(String(36), ForeignKey("runs.id", ondelete="SET NULL"), nullable=True)
    stage = Column(String(50), default="NONE", nullable=False)  # NONE, STAGING, PRODUCTION, ARCHIVED
    framework = Column(String(50), nullable=False)  # scikit-learn, xgboost, lightgbm, pytorch, onnx
    artifact_uri = Column(String(500), nullable=False)
    checksum = Column(String(64), nullable=False)
    input_schema = Column(JSON, nullable=True)
    output_schema = Column(JSON, nullable=True)
    metrics = Column(JSON, default=dict, nullable=False)
    description = Column(Text, nullable=True)

    run = relationship("Run", back_populates="artifacts")
    deployments = relationship("ModelDeployment", back_populates="model_artifact", cascade="all, delete-orphan")


class ModelDeployment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Live serving endpoint deployment configuration."""

    __tablename__ = "model_deployments"

    name = Column(String(100), unique=True, index=True, nullable=False)
    model_artifact_id = Column(String(36), ForeignKey("model_artifacts.id", ondelete="CASCADE"), nullable=False)
    traffic_percentage = Column(Float, default=100.0, nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)  # ACTIVE, INACTIVE, CANARY, SHADOW
    min_replicas = Column(Integer, default=1, nullable=False)
    max_replicas = Column(Integer, default=5, nullable=False)

    model_artifact = relationship("ModelArtifact", back_populates="deployments")
