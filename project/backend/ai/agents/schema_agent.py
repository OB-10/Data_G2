import json
from google import genai

from backend.config import settings
from backend.database.schema_manager import (
    apply_schema_sql,
    parse_schema_description,
    schema_registry,
    DatabaseSchema,
)
from backend.database.connection import SessionLocal


class SchemaAgent:

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def generate_schema(self, user_request: str, row_count: int = 100):

        prompt = f"""
You are an expert MySQL database architect.

User Request:
{user_request}

Generate complete database schema.

Return STRICT JSON:
{{
"database_name": "",
"ddl_sql": "",
"tables": []
}}
"""

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt
        )

        content = response.text

        schema_json = json.loads(content)

        ddl_sql = schema_json.get("ddl_sql", "")
        db_schema: DatabaseSchema = parse_schema_description(schema_json)

        db = SessionLocal()
        try:
            apply_schema_sql(db, ddl_sql)
        finally:
            db.close()

        schema_registry.set_schema(db_schema)

        return schema_json


schema_agent = SchemaAgent()