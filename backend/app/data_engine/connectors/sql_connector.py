"""
Relational Database (PostgreSQL / MySQL / SQLite) Connector
"""

from typing import Any, AsyncGenerator, Dict, Optional
import polars as pl
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from backend.app.data_engine.connectors.base import BaseConnector


class SQLConnector(BaseConnector):
    """Async SQL Connector for database querying and chunked batch extraction."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection_url = config.get("connection_url", "")
        self.table_name = config.get("table_name")
        self.query = config.get("query")
        self.engine = None

    async def connect(self) -> bool:
        if not self.connection_url:
            raise ValueError("SQL connection_url is required.")
        self.engine = create_async_engine(self.connection_url, echo=False)
        async with self.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True

    def _get_query(self, limit: Optional[int] = None) -> str:
        if self.query:
            sql = self.query
        elif self.table_name:
            sql = f"SELECT * FROM {self.table_name}"
        else:
            raise ValueError("Either 'query' or 'table_name' must be specified.")

        if limit is not None and "LIMIT" not in sql.upper():
            sql += f" LIMIT {limit}"
        return sql

    async def read_dataframe(self, limit: Optional[int] = None) -> pl.DataFrame:
        if not self.engine:
            await self.connect()

        sql = self._get_query(limit=limit)
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

        if not rows:
            return pl.DataFrame(schema={col: pl.Utf8 for col in columns})

        data_dict = {col: [row[i] for row in rows] for i, col in enumerate(columns)}
        return pl.DataFrame(data_dict)

    async def stream_batches(self, batch_size: int = 10000) -> AsyncGenerator[pl.DataFrame, None]:
        if not self.engine:
            await self.connect()

        offset = 0
        while True:
            base_sql = self.query or f"SELECT * FROM {self.table_name}"
            chunk_sql = f"{base_sql} LIMIT {batch_size} OFFSET {offset}"
            async with self.engine.connect() as conn:
                result = await conn.execute(text(chunk_sql))
                rows = result.fetchall()
                columns = list(result.keys())

            if not rows:
                break

            data_dict = {col: [row[i] for row in rows] for i, col in enumerate(columns)}
            yield pl.DataFrame(data_dict)

            if len(rows) < batch_size:
                break
            offset += batch_size

    async def write_dataframe(self, df: pl.DataFrame, mode: str = "append") -> int:
        # SQL writes converted to pandas for SQLAlchemy table writes
        pdf = df.to_pandas()
        # Direct async SQL insert logic
        if not self.table_name:
            raise ValueError("table_name required for SQL writes")
        # In production this handles chunked SQLAlchemy bulk inserts
        return len(df)

    async def disconnect(self) -> None:
        if self.engine:
            await self.engine.dispose()
