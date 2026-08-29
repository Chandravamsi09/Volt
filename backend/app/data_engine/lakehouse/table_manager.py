"""
Lakehouse Partition Table & Snapshot Manifest Manager
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import polars as pl
from backend.app.core.config import settings
from backend.app.core.exceptions import ValidationError


class LakehouseTableManager:
    """Manages versioned, partitioned Parquet lakehouse tables with metadata manifests."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.DATA_LAKE_PATH)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_table_dir(self, table_name: str) -> Path:
        table_dir = self.base_path / table_name
        table_dir.mkdir(parents=True, exist_ok=True)
        return table_dir

    def _get_manifest_path(self, table_name: str) -> Path:
        return self._get_table_dir(table_name) / "_manifest.json"

    def _load_manifest(self, table_name: str) -> Dict[str, Any]:
        manifest_file = self._get_manifest_path(table_name)
        if manifest_file.exists():
            with open(manifest_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "table_name": table_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "versions": [],
            "current_version": 0,
            "total_rows": 0,
            "partition_keys": [],
        }

    def _save_manifest(self, table_name: str, manifest: Dict[str, Any]) -> None:
        manifest_file = self._get_manifest_path(table_name)
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def write_table(
        self,
        table_name: str,
        df: pl.DataFrame,
        mode: str = "append",
        partition_by: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Write DataFrame into lakehouse table with snapshot versioning."""
        table_dir = self._get_table_dir(table_name)
        manifest = self._load_manifest(table_name)

        version_num = manifest["current_version"] + 1
        snapshot_id = str(uuid.uuid4())[:8]
        file_name = f"part-{version_num:05d}-{snapshot_id}.parquet"
        file_path = table_dir / file_name

        df.write_parquet(file_path, compression="zstd")

        version_meta = {
            "version": version_num,
            "snapshot_id": snapshot_id,
            "file_name": file_name,
            "row_count": len(df),
            "columns": df.columns,
            "mode": mode,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if mode == "overwrite":
            # Retain history in manifest but active files reset
            manifest["versions"] = [version_meta]
            manifest["total_rows"] = len(df)
        else:
            manifest["versions"].append(version_meta)
            manifest["total_rows"] += len(df)

        manifest["current_version"] = version_num
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        if partition_by:
            manifest["partition_keys"] = partition_by

        self._save_manifest(table_name, manifest)
        return version_meta

    def read_table(self, table_name: str, version: Optional[int] = None) -> pl.DataFrame:
        """Read active or point-in-time snapshot of lakehouse table."""
        table_dir = self._get_table_dir(table_name)
        manifest = self._load_manifest(table_name)

        if not manifest["versions"]:
            return pl.DataFrame()

        if version is not None:
            # Point in time query
            target_versions = [v for v in manifest["versions"] if v["version"] <= version]
            if not target_versions:
                raise ValidationError(f"No table versions found <= {version}")
        else:
            target_versions = manifest["versions"]

        files_to_read = [table_dir / v["file_name"] for v in target_versions if (table_dir / v["file_name"]).exists()]
        if not files_to_read:
            return pl.DataFrame()

        # Read and concatenate
        dfs = [pl.read_parquet(f) for f in files_to_read]
        return pl.concat(dfs, how="vertical_relaxed") if len(dfs) > 1 else dfs[0]

    def list_tables(self) -> List[Dict[str, Any]]:
        """List all available lakehouse tables and metadata."""
        tables = []
        for p in self.base_path.iterdir():
            if p.is_dir():
                manifest_file = p / "_manifest.json"
                if manifest_file.exists():
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        tables.append(json.load(f))
        return tables
