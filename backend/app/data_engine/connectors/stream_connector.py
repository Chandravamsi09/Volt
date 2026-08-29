"""
Real-Time Event Stream Consumer & Dead-Letter Queue (DLQ) Handler
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
import polars as pl
from backend.app.data_engine.connectors.base import BaseConnector

logger = logging.getLogger("volt.stream_connector")


class StreamConnector(BaseConnector):
    """High-throughput event consumer with in-memory buffer, batch windowing & DLQ."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.topic = config.get("topic", "default-stream")
        self.buffer_size = config.get("buffer_size", 5000)
        self.flush_interval_seconds = config.get("flush_interval_seconds", 1.0)
        self._buffer: List[Dict[str, Any]] = []
        self._dlq: List[Dict[str, Any]] = []
        self._is_running = False
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        self._is_running = True
        return True

    async def push_event(self, event: Dict[str, Any]) -> bool:
        """Receive an incoming single event into buffer."""
        async with self._lock:
            self._buffer.append(event)
            return True

    async def push_dlq(self, event: Dict[str, Any], reason: str) -> None:
        """Route malformed or rejected records to the Dead-Letter Queue."""
        dlq_record = {
            "payload": event,
            "rejection_reason": reason,
            "topic": self.topic,
        }
        async with self._lock:
            self._dlq.append(dlq_record)
        logger.warning(f"Routed record to DLQ for topic {self.topic}: {reason}")

    async def read_dataframe(self, limit: Optional[int] = None) -> pl.DataFrame:
        async with self._lock:
            if not self._buffer:
                return pl.DataFrame()
            data = list(self._buffer)
            self._buffer.clear()

        if limit is not None and limit > 0:
            data = data[:limit]
        return pl.DataFrame(data)

    async def stream_batches(self, batch_size: int = 1000) -> AsyncGenerator[pl.DataFrame, None]:
        while self._is_running:
            await asyncio.sleep(self.flush_interval_seconds)
            async with self._lock:
                if not self._buffer:
                    continue
                to_process = self._buffer[:batch_size]
                self._buffer = self._buffer[batch_size:]

            if to_process:
                yield pl.DataFrame(to_process)

    async def write_dataframe(self, df: pl.DataFrame, mode: str = "append") -> int:
        records = df.to_dicts()
        async with self._lock:
            self._buffer.extend(records)
        return len(records)

    async def get_dlq_records(self) -> List[Dict[str, Any]]:
        async with self._lock:
            return list(self._dlq)

    async def disconnect(self) -> None:
        self._is_running = False
