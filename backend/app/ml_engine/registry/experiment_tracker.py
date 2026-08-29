"""
Experiment Tracking & Performance Metrics Logger
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class MetricPoint:
    name: str
    value: float
    step: int
    timestamp: str


@dataclass
class ExperimentRunContext:
    run_id: str
    experiment_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, List[MetricPoint]] = field(default_factory=dict)
    summary_metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    status: str = "RUNNING"
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = None


class ExperimentTracker:
    """Tracks training runs, hyperparameter sweeps, metric steps, and performance curves."""

    def __init__(self, tracking_dir: str = "./data/experiments"):
        self.tracking_dir = Path(tracking_dir)
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        self._active_runs: Dict[str, ExperimentRunContext] = {}

    def start_run(
        self,
        experiment_name: str,
        run_name: str,
        tags: Optional[List[str]] = None,
    ) -> ExperimentRunContext:
        run_id = f"{experiment_name}-{run_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        run_ctx = ExperimentRunContext(
            run_id=run_id,
            experiment_name=experiment_name,
            tags=tags or [],
        )
        self._active_runs[run_id] = run_ctx
        return run_ctx

    def log_param(self, run_id: str, key: str, value: Any) -> None:
        if run_id in self._active_runs:
            self._active_runs[run_id].parameters[key] = value

    def log_params(self, run_id: str, params: Dict[str, Any]) -> None:
        if run_id in self._active_runs:
            self._active_runs[run_id].parameters.update(params)

    def log_metric(self, run_id: str, key: str, value: float, step: int = 0) -> None:
        if run_id in self._active_runs:
            pt = MetricPoint(
                name=key,
                value=float(value),
                step=step,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            if key not in self._active_runs[run_id].metrics:
                self._active_runs[run_id].metrics[key] = []
            self._active_runs[run_id].metrics[key].append(pt)
            self._active_runs[run_id].summary_metrics[key] = float(value)

    def end_run(self, run_id: str, status: str = "COMPLETED") -> ExperimentRunContext:
        if run_id not in self._active_runs:
            raise KeyError(f"Run ID '{run_id}' not found.")
        ctx = self._active_runs[run_id]
        ctx.status = status
        ctx.end_time = datetime.now(timezone.utc).isoformat()

        # Save run summary to disk
        exp_dir = self.tracking_dir / ctx.experiment_name
        exp_dir.mkdir(parents=True, exist_ok=True)
        run_file = exp_dir / f"{run_id}.json"

        # Serialize metrics points
        serializable_metrics = {
            k: [p.__dict__ for p in v] for k, v in ctx.metrics.items()
        }
        payload = {
            "run_id": ctx.run_id,
            "experiment_name": ctx.experiment_name,
            "parameters": ctx.parameters,
            "summary_metrics": ctx.summary_metrics,
            "metrics": serializable_metrics,
            "tags": ctx.tags,
            "status": ctx.status,
            "start_time": ctx.start_time,
            "end_time": ctx.end_time,
        }
        with open(run_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return ctx
