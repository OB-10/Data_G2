from google import genai

from backend.ai.rag.schema_retriever import get_relevant_schema_text
from backend.config import settings


class SQLAgent:

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def generate_sql(self, question: str):

        schema_context = get_relevant_schema_text(question)

        prompt = f"""
You are an expert MySQL engineer.

Database Schema:
{schema_context}

User Question:
{question}

Generate ONLY SQL SELECT query.
Do NOT explain.
"""

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt
        )

        sql = response.text.strip().rstrip(";")

        return sql


sql_agent = SQLAgent()