"""
Real-Time Inference Engine (ONNX Runtime & Native Fast Predictor)
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
from backend.app.core.exceptions import ModelRegistryError


@dataclass
class PredictionOutput:
    model_name: str
    model_version: str
    predictions: List[Any]
    probabilities: Optional[List[List[float]]]
    latency_ms: float
    metadata: Dict[str, Any]


class ModelInferenceEngine:
    """In-memory model pool managing active ONNX Runtime sessions and predictors."""

    def __init__(self):
        self._onnx_sessions: Dict[str, Any] = {}
        self._native_models: Dict[str, Any] = {}

    def _session_key(self, name: str, version: str) -> str:
        return f"{name}:{version}"

    def load_model(self, name: str, version: str, artifact_path: str, framework: str = "onnx") -> None:
        """Load model into memory pool."""
        key = self._session_key(name, version)
        path = Path(artifact_path)
        if not path.exists():
            raise ModelRegistryError(f"Artifact file not found: {artifact_path}")

        if framework == "onnx" and path.suffix == ".onnx":
            try:
                import onnxruntime as ort
                session = ort.InferenceSession(
                    str(path),
                    providers=["CPUExecutionProvider"],
                )
                self._onnx_sessions[key] = session
                return
            except Exception:
                pass

        # Fallback to joblib native loading
        import joblib
        loaded = joblib.load(str(path))
        self._native_models[key] = loaded

    def predict(
        self,
        name: str,
        version: str,
        features: Union[List[List[float]], np.ndarray],
    ) -> PredictionOutput:
        """Execute real-time prediction with sub-5ms latency measurement."""
        key = self._session_key(name, version)
        start_time = time.perf_counter()

        arr = np.array(features, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        probabilities = None

        if key in self._onnx_sessions:
            session = self._onnx_sessions[key]
            input_name = session.get_inputs()[0].name
            raw_outputs = session.run(None, {input_name: arr})
            preds = raw_outputs[0].tolist()
        elif key in self._native_models:
            model_obj = self._native_models[key]
            if hasattr(model_obj, "predict"):
                preds = model_obj.predict(arr).tolist()
                if hasattr(model_obj, "predict_proba"):
                    probabilities = model_obj.predict_proba(arr).tolist()
            elif isinstance(model_obj, dict) and "model" in model_obj:
                preds = model_obj["model"].predict(arr).tolist()
                if hasattr(model_obj["model"], "predict_proba"):
                    probabilities = model_obj["model"].predict_proba(arr).tolist()
            else:
                preds = [0] * len(arr)
        else:
            raise ModelRegistryError(f"Model '{name}:{version}' is not loaded in inference engine.")

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return PredictionOutput(
            model_name=name,
            model_version=version,
            predictions=preds,
            probabilities=probabilities,
            latency_ms=round(duration_ms, 3),
            metadata={"batch_size": len(arr)},
        )

    def unload_model(self, name: str, version: str) -> None:
        key = self._session_key(name, version)
        self._onnx_sessions.pop(key, None)
        self._native_models.pop(key, None)


# Global serving inference engine
inference_engine = ModelInferenceEngine()
