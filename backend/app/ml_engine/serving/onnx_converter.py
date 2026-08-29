"""
Automated Model-to-ONNX Graph Serialization & Optimizer
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import torch
from backend.app.core.exceptions import ModelRegistryError


class ONNXConverter:
    """Converts PyTorch and Scikit-Learn models to high-throughput ONNX graphs."""

    @staticmethod
    def convert_pytorch_to_onnx(
        model: torch.nn.Module,
        input_dim: int,
        output_onnx_path: str,
        dynamic_batch: bool = True,
    ) -> str:
        """Export PyTorch Module to ONNX graph."""
        Path(output_onnx_path).parent.mkdir(parents=True, exist_ok=True)
        model.eval()
        dummy_input = torch.randn(1, input_dim, dtype=torch.float32)

        dynamic_axes = {"input": {0: "batch_size"}, "output": {0: "batch_size"}} if dynamic_batch else None

        torch.onnx.export(
            model,
            dummy_input,
            output_onnx_path,
            export_params=True,
            opset_version=14,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["output"],
            dynamic_axes=dynamic_axes,
        )
        return output_onnx_path

    @staticmethod
    def convert_sklearn_to_onnx(
        model: Any,
        num_features: int,
        output_onnx_path: str,
    ) -> str:
        """Convert Scikit-Learn model to ONNX using skl2onnx if installed, or fallback."""
        Path(output_onnx_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            from skl2onnx import convert_sklearn
            from skl2onnx.common.data_types import FloatTensorType

            initial_type = [("float_input", FloatTensorType([None, num_features]))]
            onx = convert_sklearn(model, initial_types=initial_type)
            with open(output_onnx_path, "wb") as f:
                f.write(onx.SerializeToString())
            return output_onnx_path
        except ImportError:
            # When skl2onnx is optional, save joblib proxy
            import joblib
            joblib.dump(model, output_onnx_path)
            return output_onnx_path
