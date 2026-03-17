from google import genai

from backend.ai.rag.schema_retriever import get_relevant_schema_text
from backend.config import settings


class SQLCorrectionAgent:
    """
    Fixes wrong SQL query using Gemini + Schema context + Error message
    """

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def fix_query(self, sql_query: str, error_message: str, user_question: str):

        schema_context = get_relevant_schema_text(user_question)

        prompt = f"""
You are a senior MySQL engineer.

Database Schema:
{schema_context}

User Question:
{user_question}

Wrong SQL Query:
{sql_query}

Error Message:
{error_message}

Generate ONLY corrected SQL SELECT query.
Do NOT explain.
"""

        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt
        )

        corrected_sql = response.text.strip().rstrip(";")

        return corrected_sql


correction_agent = SQLCorrectionAgent()