"""
Base Abstract Data Connector
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional
import polars as pl


class BaseConnector(ABC):
    """Abstract interface for all source & sink data connectors in Volt."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection and verify credentials."""
        pass

    @abstractmethod
    async def read_dataframe(self, limit: Optional[int] = None) -> pl.DataFrame:
        """Read data into a memory-efficient Polars DataFrame."""
        pass

    @abstractmethod
    async def stream_batches(self, batch_size: int = 10000) -> AsyncGenerator[pl.DataFrame, None]:
        """Stream chunks of data asynchronously for large datasets."""
        pass

    @abstractmethod
    async def write_dataframe(self, df: pl.DataFrame, mode: str = "append") -> int:
        """Write DataFrame to target storage. Returns count of written rows."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Gracefully release connection resources."""
        pass
