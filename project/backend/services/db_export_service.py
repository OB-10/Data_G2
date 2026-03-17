from typing import Optional
import csv
import os
import tempfile

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database.schema_manager import DatabaseSchema


def export_primary_table_to_csv(
    db: Session, schema: Optional[DatabaseSchema]
) -> Optional[str]:
    """
    Export the primary table of the current schema to a CSV file.
    Returns the path to the CSV file or None if no schema/table.
    """
    if schema is None or schema.primary_table is None:
        return None

    table_name = schema.primary_table.name
    result = db.execute(text(f"SELECT * FROM {table_name}"))
    columns = list(result.keys())

    tmp_dir = tempfile.gettempdir()
    file_path = os.path.join(tmp_dir, f"{schema.name}_{table_name}.csv")

    with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        for row in result.fetchall():
            writer.writerow(list(row))

    return file_path

