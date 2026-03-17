from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.ai.agents.sql_agent import sql_agent
from backend.ai.agents.schema_agent import schema_agent
from backend.ai.agents.correction_agent import correction_agent
from backend.database.connection import get_db
from backend.database.query_executor import execute_select_query, UnsafeQueryError
from backend.database.schema_manager import schema_registry
from backend.services.data_generator import populate_with_fake_data
from backend.services.er_diagram_service import generate_er_diagram
from backend.services.db_export_service import export_primary_table_to_csv


router = APIRouter()


class GenerateDatabaseRequest(BaseModel):
    request: str
    rows: int = 100


class QueryRequest(BaseModel):
    question: str


@router.post("/generate-database")
def generate_database(
    payload: GenerateDatabaseRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate database schema from natural language, create tables,
    and populate with synthetic data.
    """
    schema_json = schema_agent.generate_schema(
        user_request=payload.request, row_count=payload.rows
    )

    # Populate primary table with fake data
    schema = schema_registry.get_schema()
    if schema is not None:
        populate_with_fake_data(db, schema, rows_per_primary=payload.rows)

    return {"schema": schema_json}


@router.post("/query")
def query(payload: QueryRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Conversational natural language to SQL endpoint.
    Returns SQL query, raw result, and simple explanation.
    """
    question = payload.question
    sql_query = sql_agent.generate_sql(question)

    try:
        columns, rows = execute_select_query(db, sql_query)
    except UnsafeQueryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Try correction agent once
        corrected_sql = correction_agent.fix_query(
            sql_query=sql_query, error_message=str(e), user_question=question
        )
        try:
            columns, rows = execute_select_query(db, corrected_sql)
            sql_query = corrected_sql
        except Exception as inner_e:
            raise HTTPException(status_code=500, detail=f"Query failed: {inner_e}")

    explanation = (
        "The query was generated based on your question and the current database schema."
    )

    return {"sql_query": sql_query, "columns": columns, "rows": rows, "explanation": explanation}


@router.get("/er-diagram")
def er_diagram() -> Any:
    """
    Return the ER diagram image for the current schema, if available.
    """
    schema = schema_registry.get_schema()
    png_path = generate_er_diagram(schema)
    if not png_path:
        raise HTTPException(status_code=404, detail="No schema available.")
    return FileResponse(png_path, media_type="image/png", filename="er_diagram.png")


@router.get("/download-db")
def download_db(db: Session = Depends(get_db)) -> Any:
    """
    Download the primary table of the current schema as CSV.
    """
    schema = schema_registry.get_schema()
    file_path = export_primary_table_to_csv(db, schema)
    if not file_path:
        raise HTTPException(status_code=404, detail="No data available to export.")
    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=file_path.split("\\")[-1].split("/")[-1],
    )

