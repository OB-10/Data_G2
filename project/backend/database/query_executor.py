from typing import Any, List, Dict, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session


class UnsafeQueryError(Exception):
    """Raised when a query appears unsafe (non-SELECT etc.)."""


def _ensure_safe_select(sql: str) -> None:
    """
    Basic safety check to ensure only SELECT queries are executed
    in the conversational interface.
    """
    normalized = " ".join(sql.strip().lower().split())
    if not normalized.startswith("select"):
        raise UnsafeQueryError("Only SELECT queries are allowed for this endpoint.")


def execute_select_query(db: Session, sql: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Execute a SELECT query safely and return column names and rows as dicts.
    """
    _ensure_safe_select(sql)
    result = db.execute(text(sql))
    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchall()]
    return columns, rows

