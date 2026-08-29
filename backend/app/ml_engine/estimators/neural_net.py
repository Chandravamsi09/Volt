"""
PyTorch Deep Neural Network (MLP / Residual Tabular Architecture)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from backend.app.ml_engine.estimators.base_estimator import BaseEstimator


class TabularMLPNet(nn.Module):
    """Multi-Layer Perceptron with BatchNorm, LeakyReLU, and Dropout."""

    def __init__(self, input_dim: int, hidden_dims: List[int], output_dim: int, dropout: float = 0.1):
        super().__init__()
        layers = []
        in_d = input_dim
        for h_d in hidden_dims:
            layers.append(nn.Linear(in_d, h_d))
            layers.append(nn.BatchNorm1d(h_d))
            layers.append(nn.LeakyReLU(0.1))
            layers.append(nn.Dropout(dropout))
            in_d = h_d
        layers.append(nn.Linear(in_d, output_dim))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class PyTorchClassifier(BaseEstimator):
    """Deep Learning Classifier for complex tabular representations."""

    def __init__(
        self,
        hidden_dims: Optional[List[int]] = None,
        learning_rate: float = 0.001,
        batch_size: int = 64,
        epochs: int = 20,
        dropout: float = 0.1,
    ):
        self.hidden_dims = hidden_dims or [128, 64]
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.dropout = dropout
        super().__init__({
            "hidden_dims": self.hidden_dims,
            "learning_rate": self.learning_rate,
            "batch_size": self.batch_size,
            "epochs": self.epochs,
            "dropout": self.dropout,
        })
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net = None
        self.num_classes = 2

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None) -> "PyTorchClassifier":
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        unique_classes = np.unique(y)
        self.num_classes = len(unique_classes)

        input_dim = X.shape[1]
        self.net = TabularMLPNet(
            input_dim=input_dim,
            hidden_dims=self.hidden_dims,
            output_dim=self.num_classes,
            dropout=self.dropout,
        ).to(self.device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(self.net.parameters(), lr=self.learning_rate, weight_decay=1e-4)

        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.long)
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        self.net.train()
        for epoch in range(self.epochs):
            for batch_x, batch_y in loader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                optimizer.zero_grad()
                out = self.net(batch_x)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()

        self._is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self._is_trained or self.net is None:
            raise RuntimeError("Model must be trained before predict_proba().")
        self.net.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(X, dtype=torch.float32).to(self.device)
            logits = self.net(X_tensor)
            proba = torch.softmax(logits, dim=-1).cpu().numpy()
        return proba

    def predict(self, X: np.ndarray) -> np.ndarray:
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        preds = self.predict(X)
        from sklearn.metrics import accuracy_score, f1_score
        return {
            "accuracy": float(accuracy_score(y, preds)),
            "f1": float(f1_score(y, preds, average="weighted", zero_division=0)),
        }

    def save(self, filepath: str) -> None:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "config": self.config,
            "feature_names": self.feature_names,
            "num_classes": self.num_classes,
            "state_dict": self.net.state_dict() if self.net else None,
            "_is_trained": self._is_trained,
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> "PyTorchClassifier":
        data = torch.load(filepath, map_location="cpu")
        inst = cls(**data["config"])
        inst.feature_names = data.get("feature_names", [])
        inst.num_classes = data.get("num_classes", 2)
        inst._is_trained = data.get("_is_trained", False)
        if data.get("state_dict"):
            inst.net = TabularMLPNet(
                input_dim=len(inst.feature_names),
                hidden_dims=inst.hidden_dims,
                output_dim=inst.num_classes,
                dropout=inst.dropout,
            )
            inst.net.load_state_dict(data["state_dict"])
            inst.net.eval()
        return inst
