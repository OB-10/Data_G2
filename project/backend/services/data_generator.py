from typing import Any, Dict, List
import random

from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database.schema_manager import DatabaseSchema


fake = Faker()


def _fake_value_for_type(column_name: str, sql_type: str) -> Any:
    """
    Generate a synthetic value based on a crude interpretation of SQL type
    and column name. This is heuristic but works well for demos.
    """
    type_upper = sql_type.upper()
    name_lower = column_name.lower()

    if "int" in type_upper:
        if "price" in name_lower or "amount" in name_lower or "cost" in name_lower:
            return random.randint(1000, 10000)
        if "rooms" in name_lower or "capacity" in name_lower:
            return random.randint(1, 10)
        return random.randint(0, 100)
    if "float" in type_upper or "double" in type_upper or "decimal" in type_upper:
        if "rating" in name_lower or "score" in name_lower:
            return round(random.uniform(1.0, 5.0), 1)
        return round(random.uniform(0.0, 100.0), 2)
    if "date" in type_upper:
        return fake.date_between(start_date="-2y", end_date="+1y")
    if "time" in type_upper:
        return fake.date_time_this_year()
    # Fallback to string types
    if "name" in name_lower and "hotel" in name_lower:
        return fake.company() + " Hotel"
    if "city" in name_lower or "location" in name_lower:
        return fake.city()
    if "email" in name_lower:
        return fake.email()
    if "phone" in name_lower or "mobile" in name_lower:
        return fake.phone_number()
    if "address" in name_lower:
        return fake.address()
    if "description" in name_lower or "desc" in name_lower:
        return fake.sentence(nb_words=12)
    return fake.word()


def populate_with_fake_data(
    db: Session, schema: DatabaseSchema, rows_per_primary: int = 100
) -> None:
    """
    Insert synthetic rows into the primary table (and potentially others).
    Only handles simple, non-FK relationships for now.
    """
    primary = schema.primary_table
    if primary is None:
        return

    cols = [c for c in primary.columns if not c.is_primary_key or "auto_increment" not in c.type.lower()]
    col_names = [c.name for c in cols]
    placeholders = ", ".join([f":{name}" for name in col_names])

    insert_sql = f"INSERT INTO {primary.name} ({', '.join(col_names)}) VALUES ({placeholders})"

    for _ in range(rows_per_primary):
        values: Dict[str, Any] = {}
        for c in cols:
            values[c.name] = _fake_value_for_type(c.name, c.type)
        db.execute(text(insert_sql), values)

    db.commit()

