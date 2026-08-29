"""
Lakehouse Pipelines, Tables & SQL Query API Endpoints
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
import polars as pl
from pydantic import BaseModel
from backend.app.data_engine.lakehouse.query_engine import DuckDBQueryEngine
from backend.app.data_engine.lakehouse.table_manager import LakehouseTableManager
from backend.app.schemas.common import StandardResponse

router = APIRouter(prefix="/pipelines", tags=["Data Pipelines & Lakehouse"])


class QueryRequest(BaseModel):
    sql: str


class TableIngestRequest(BaseModel):
    table_name: str
    data: List[Dict[str, Any]]
    mode: str = "append"


@router.get("/tables", response_model=StandardResponse[List[Dict[str, Any]]])
async def list_lakehouse_tables():
    """List all available lakehouse tables and metadata."""
    mgr = LakehouseTableManager()
    tables = mgr.list_tables()
    return StandardResponse(data=tables, message=f"Retrieved {len(tables)} tables")


@router.post("/tables/ingest", response_model=StandardResponse[Dict[str, Any]])
async def ingest_records_to_table(payload: TableIngestRequest):
    """Directly ingest records into a lakehouse table."""
    if not payload.data:
        raise HTTPException(status_code=400, detail="Data payload cannot be empty")

    df = pl.DataFrame(payload.data)
    mgr = LakehouseTableManager()
    meta = mgr.write_table(table_name=payload.table_name, df=df, mode=payload.mode)

    return StandardResponse(
        data=meta,
        message=f"Ingested {len(df)} records into table '{payload.table_name}'",
    )


@router.post("/query", response_model=StandardResponse[Dict[str, Any]])
async def run_sql_query(query_in: QueryRequest):
    """Execute arbitrary analytical SQL query over the Lakehouse via DuckDB."""
    query_engine = DuckDBQueryEngine()
    try:
        df = query_engine.execute_query(query_in.sql)
        records = df.to_dicts()
        return StandardResponse(
            data={
                "row_count": len(records),
                "columns": df.columns,
                "records": records[:1000],  # Capped at 1000 for response safety
            },
            message="Query executed successfully",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"SQL Query Error: {str(exc)}")
    finally:
        query_engine.close()
