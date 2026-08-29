"""
Optuna Automated Hyperparameter Optimization Engine
"""

from typing import Any, Callable, Dict, List, Optional
import numpy as np
import optuna
from sklearn.model_selection import cross_val_score
from backend.app.ml_engine.estimators.tabular import TabularClassifier

# Suppress verbose Optuna logging in production
optuna.logging.set_verbosity(optuna.logging.WARNING)


class HyperparameterTuner:
    """Automated Bayesian hyperparameter optimization."""

    def __init__(self, n_trials: int = 20, timeout_seconds: int = 300):
        self.n_trials = n_trials
        self.timeout_seconds = timeout_seconds
        self.best_params: Dict[str, Any] = {}
        self.best_score: float = 0.0

    def optimize_tabular_classifier(
        self,
        X: np.ndarray,
        y: np.ndarray,
        algorithm: str = "gradient_boosting",
        cv_folds: int = 3,
    ) -> Dict[str, Any]:
        """Tune hyperparameter space for TabularClassifier using cross-validation."""

        def objective(trial: optuna.Trial) -> float:
            if algorithm == "random_forest":
                n_estimators = trial.suggest_int("n_estimators", 20, 200, step=20)
                max_depth = trial.suggest_int("max_depth", 3, 15)
                clf = TabularClassifier(
                    algorithm="random_forest",
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                )
            else:
                n_estimators = trial.suggest_int("n_estimators", 20, 200, step=20)
                max_depth = trial.suggest_int("max_depth", 2, 8)
                learning_rate = trial.suggest_float("learning_rate", 0.01, 0.3, log=True)
                clf = TabularClassifier(
                    algorithm="gradient_boosting",
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    learning_rate=learning_rate,
                )

            # 3-Fold Cross Validation
            scores = cross_val_score(clf.model, X, y, cv=cv_folds, scoring="accuracy")
            return float(scores.mean())

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, timeout=self.timeout_seconds)

        self.best_params = study.best_params
        self.best_params["algorithm"] = algorithm
        self.best_score = float(study.best_value)

        return {
            "best_params": self.best_params,
            "best_score": self.best_score,
            "total_trials": len(study.trials),
        }
