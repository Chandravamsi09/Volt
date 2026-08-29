"""
High-Performance File & Lakehouse Connector (Parquet, CSV, JSON, Arrow)
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional
import polars as pl
from backend.app.core.exceptions import ValidationError
from backend.app.data_engine.connectors.base import BaseConnector


class FileConnector(BaseConnector):
    """Connector for local or mounted object storage files (Parquet, CSV, IPC/Arrow, JSON)."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.file_path = Path(config.get("file_path", ""))
        self.file_format = config.get("format", "parquet").lower()

    async def connect(self) -> bool:
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
        return True

    async def read_dataframe(self, limit: Optional[int] = None) -> pl.DataFrame:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Source file not found at: {self.file_path}")

        if self.file_format == "parquet":
            df = pl.read_parquet(self.file_path)
        elif self.file_format == "csv":
            df = pl.read_csv(self.file_path)
        elif self.file_format in ["json", "ndjson"]:
            df = pl.read_ndjson(self.file_path)
        elif self.file_format in ["ipc", "arrow", "feather"]:
            df = pl.read_ipc(self.file_path)
        else:
            raise ValidationError(f"Unsupported file format: {self.file_format}")

        if limit is not None and limit > 0:
            df = df.head(limit)
        return df

    async def stream_batches(self, batch_size: int = 10000) -> AsyncGenerator[pl.DataFrame, None]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"Source file not found at: {self.file_path}")

        if self.file_format == "parquet":
            # Lazy scan with streaming batches
            lazy_df = pl.scan_parquet(self.file_path)
            total_rows = lazy_df.select(pl.len()).collect().item()
            for offset in range(0, total_rows, batch_size):
                chunk = lazy_df.slice(offset, batch_size).collect()
                yield chunk
        elif self.file_format == "csv":
            reader = pl.read_csv_batched(self.file_path, batch_size=batch_size)
            batches = reader.next_batches(1)
            while batches:
                for batch in batches:
                    yield batch
                batches = reader.next_batches(1)
        else:
            df = await self.read_dataframe()
            for offset in range(0, len(df), batch_size):
                yield df.slice(offset, batch_size)

    async def write_dataframe(self, df: pl.DataFrame, mode: str = "append") -> int:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if mode == "append" and self.file_path.exists():
            existing_df = await self.read_dataframe()
            final_df = pl.concat([existing_df, df], how="vertical_relaxed")
        else:
            final_df = df

        if self.file_format == "parquet":
            final_df.write_parquet(self.file_path, compression="zstd")
        elif self.file_format == "csv":
            final_df.write_csv(self.file_path)
        elif self.file_format in ["json", "ndjson"]:
            final_df.write_ndjson(self.file_path)
        elif self.file_format in ["ipc", "arrow", "feather"]:
            final_df.write_ipc(self.file_path, compression="zstd")

        return len(df)

    async def disconnect(self) -> None:
        pass
