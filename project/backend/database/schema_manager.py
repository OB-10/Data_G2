from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class ColumnSchema:
    name: str
    type: str
    nullable: bool = True
    is_primary_key: bool = False
    references: Optional[str] = None  # "other_table.column"


@dataclass
class TableSchema:
    name: str
    columns: List[ColumnSchema] = field(default_factory=list)


@dataclass
class DatabaseSchema:
    name: str
    tables: List[TableSchema] = field(default_factory=list)

    @property
    def primary_table(self) -> Optional[TableSchema]:
        """Return the first table as primary for exports/visualization."""
        return self.tables[0] if self.tables else None


class SchemaRegistry:
    """
    In-memory registry of the current active generated database schema.
    This keeps the backend stateless with respect to storage but stateful
    for a running process, which is sufficient for a single-user demo.
    """

    def __init__(self) -> None:
        self._schema: Optional[DatabaseSchema] = None

    def set_schema(self, schema: DatabaseSchema) -> None:
        self._schema = schema

    def get_schema(self) -> Optional[DatabaseSchema]:
        return self._schema


schema_registry = SchemaRegistry()


def apply_schema_sql(db: Session, ddl_sql: str) -> None:
    """
    Execute DDL statements (CREATE DATABASE/TABLE) produced by the schema agent.
    Expects valid MySQL DDL; errors will bubble up to caller.
    """
    for statement in filter(None, (s.strip() for s in ddl_sql.split(";"))):
        if not statement:
            continue
        db.execute(text(statement))
    db.commit()


def parse_schema_description(schema_description: Dict) -> DatabaseSchema:
    """
    Parse a structured schema description (JSON-like dict) into DatabaseSchema.

    Expected format:
    {
      "database_name": "hotels_goa",
      "tables": [
        {
          "name": "hotels",
          "columns": [
            {
              "name": "hotel_name",
              "type": "VARCHAR(255)",
              "nullable": false,
              "is_primary_key": false
            },
            ...
          ]
        }
      ]
    }
    """
    db_name = schema_description.get("database_name", "generated_db")
    tables: List[TableSchema] = []

    for t in schema_description.get("tables", []):
        cols: List[ColumnSchema] = []
        for c in t.get("columns", []):
            cols.append(
                ColumnSchema(
                    name=c.get("name"),
                    type=c.get("type", "VARCHAR(255)"),
                    nullable=bool(c.get("nullable", True)),
                    is_primary_key=bool(c.get("is_primary_key", False)),
                    references=c.get("references"),
                )
            )
        tables.append(TableSchema(name=t.get("name"), columns=cols))

    return DatabaseSchema(name=db_name, tables=tables)

