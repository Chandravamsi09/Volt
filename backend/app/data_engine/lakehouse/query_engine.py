"""
High-Performance DuckDB Analytics & Lakehouse SQL Query Engine
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
import polars as pl
from backend.app.core.config import settings


class DuckDBQueryEngine:
    """Embedded OLAP query engine executing complex SQL across lakehouse parquet partitions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DUCKDB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        # Use memory database or persistent file
        self.conn = duckdb.connect(database=":memory:", read_only=False)
        # Configure threads for maximum multi-core throughput
        self.conn.execute("PRAGMA threads=4;")
        self.conn.execute("PRAGMA memory_limit='4GB';")

    def register_dataframe(self, view_name: str, df: pl.DataFrame) -> None:
        """Register a Polars DataFrame as a DuckDB virtual relational view."""
        arrow_table = df.to_arrow()
        self.conn.register(view_name, arrow_table)

    def register_parquet_table(self, view_name: str, parquet_glob: str) -> None:
        """Create a direct view over Parquet partitions on disk."""
        sql = f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{parquet_glob}');"
        self.conn.execute(sql)

    def execute_query(self, sql: str, params: Optional[List[Any]] = None) -> pl.DataFrame:
        """Execute arbitrary SQL and return results as high-performance Polars DataFrame."""
        if params:
            res = self.conn.execute(sql, params).arrow()
        else:
            res = self.conn.execute(sql).arrow()
        return pl.from_arrow(res)

    def profile_table(self, table_or_view: str) -> Dict[str, Any]:
        """Compute column distributions, null ratios, quantiles, and row counts."""
        count_res = self.conn.execute(f"SELECT COUNT(*) as total_rows FROM {table_or_view}").fetchone()
        total_rows = count_res[0] if count_res else 0

        summary_df = self.execute_query(f"SUMMARIZE {table_or_view}")
        return {
            "table_name": table_or_view,
            "total_rows": total_rows,
            "column_profiles": summary_df.to_dicts(),
        }

    def close(self) -> None:
        if self.conn:
            self.conn.close()
