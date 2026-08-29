"""
Asynchronous Model Training, Hyperparameter Optimization & ONNX Export Tasks
"""

import logging
from typing import Any, Dict, List, Optional
import polars as pl
from backend.app.data_engine.lakehouse.table_manager import LakehouseTableManager
from backend.app.ml_engine.registry.model_vault import ModelVault
from backend.app.ml_engine.trainers.pipeline_trainer import MLTrainingPipeline
from backend.app.ml_engine.trainers.tuner import HyperparameterTuner
from backend.app.workers.celery_app import celery_app

logger = logging.getLogger("volt.workers.training")


@celery_app.task(name="backend.app.workers.training_tasks.train_model_task", bind=True)
def train_model_task(
    self,
    table_name: str,
    feature_columns: List[str],
    target_column: str,
    model_name: str,
    version: str,
    algorithm: str = "gradient_boosting",
    hyperparameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Background task executing model training and registering artifacts in ModelVault."""
    logger.info(f"Initiating distributed training task for model '{model_name}:{version}'")
    table_mgr = LakehouseTableManager()
    df = table_mgr.read_table(table_name)

    pipeline = MLTrainingPipeline()
    estimator, metrics, run_id = pipeline.train_classification_pipeline(
        df=df,
        feature_columns=feature_columns,
        target_column=target_column,
        experiment_name=model_name,
        run_name=f"run_{version}",
        algorithm=algorithm,
        hyperparameters=hyperparameters,
    )

    # Save to temp artifact and register in Model Vault
    temp_path = f"/tmp/{model_name}_{version}.joblib"
    estimator.save(temp_path)

    vault = ModelVault()
    meta = vault.register_model(
        name=model_name,
        version=version,
        artifact_source_path=temp_path,
        framework="scikit-learn",
        metrics=metrics,
        parameters=hyperparameters or {},
        stage="STAGING",
        description=f"Automated background training task {self.request.id}",
    )

    logger.info(f"Model '{model_name}:{version}' trained successfully. Metrics: {metrics}")
    return {
        "model_name": model_name,
        "version": version,
        "run_id": run_id,
        "metrics": metrics,
        "checksum": meta.checksum,
    }
