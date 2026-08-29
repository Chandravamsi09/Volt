"""
Production Model Vault, Version Control & Cryptographic Checksum Manager
"""

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings
from backend.app.core.exceptions import ModelRegistryError


@dataclass
class ModelMetadata:
    name: str
    version: str
    framework: str
    stage: str
    checksum: str
    created_at: str
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    input_schema: Dict[str, str]
    output_schema: Dict[str, str]
    description: Optional[str] = None


class ModelVault:
    """Enterprise Model Vault managing serialized weights, ONNX graphs, and metadata."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.MODEL_VAULT_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_model_dir(self, name: str, version: str) -> Path:
        m_dir = self.base_path / name / version
        m_dir.mkdir(parents=True, exist_ok=True)
        return m_dir

    def calculate_checksum(self, file_path: Path) -> str:
        """Compute SHA256 checksum of model artifact."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def register_model(
        self,
        name: str,
        version: str,
        artifact_source_path: str,
        framework: str,
        metrics: Optional[Dict[str, float]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        input_schema: Optional[Dict[str, str]] = None,
        output_schema: Optional[Dict[str, str]] = None,
        stage: str = "NONE",
        description: Optional[str] = None,
    ) -> ModelMetadata:
        """Register, copy, checksum, and index model artifact into the vault."""
        src_path = Path(artifact_source_path)
        if not src_path.exists():
            raise ModelRegistryError(f"Artifact source path does not exist: {artifact_source_path}")

        model_dir = self._get_model_dir(name, version)
        dest_artifact_path = model_dir / src_path.name

        shutil.copy2(src_path, dest_artifact_path)
        checksum = self.calculate_checksum(dest_artifact_path)

        metadata = ModelMetadata(
            name=name,
            version=version,
            framework=framework,
            stage=stage.upper(),
            checksum=checksum,
            created_at=datetime.now(timezone.utc).isoformat(),
            metrics=metrics or {},
            parameters=parameters or {},
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            description=description,
        )

        # Save metadata JSON
        with open(model_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata.__dict__, f, indent=2)

        return metadata

    def get_model(self, name: str, version: str) -> Optional[ModelMetadata]:
        model_dir = self.base_path / name / version
        meta_file = model_dir / "metadata.json"
        if not meta_file.exists():
            return None
        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ModelMetadata(**data)

    def list_versions(self, name: str) -> List[ModelMetadata]:
        model_root = self.base_path / name
        if not model_root.exists():
            return []
        versions = []
        for v_dir in model_root.iterdir():
            if v_dir.is_dir():
                meta_file = v_dir / "metadata.json"
                if meta_file.exists():
                    with open(meta_file, "r", encoding="utf-8") as f:
                        versions.append(ModelMetadata(**json.load(f)))
        return sorted(versions, key=lambda x: x.created_at, reverse=True)

    def transition_stage(self, name: str, version: str, new_stage: str) -> ModelMetadata:
        """Promote or demote model lifecycle stage (STAGING, PRODUCTION, ARCHIVED)."""
        valid_stages = ["NONE", "STAGING", "PRODUCTION", "ARCHIVED"]
        if new_stage.upper() not in valid_stages:
            raise ModelRegistryError(f"Invalid stage '{new_stage}'. Must be one of {valid_stages}")

        meta = self.get_model(name, version)
        if not meta:
            raise ModelRegistryError(f"Model '{name}' version '{version}' not found.")

        # If promoting to PRODUCTION, archive any current production models of same name
        if new_stage.upper() == "PRODUCTION":
            all_versions = self.list_versions(name)
            for v in all_versions:
                if v.version != version and v.stage == "PRODUCTION":
                    v.stage = "ARCHIVED"
                    v_dir = self.base_path / name / v.version
                    with open(v_dir / "metadata.json", "w", encoding="utf-8") as f:
                        json.dump(v.__dict__, f, indent=2)

        meta.stage = new_stage.upper()
        model_dir = self._get_model_dir(name, version)
        with open(model_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta.__dict__, f, indent=2)

        return meta
