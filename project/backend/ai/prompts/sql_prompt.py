from langchain.prompts import PromptTemplate


SQL_PROMPT_TEMPLATE = """
You are an expert MySQL query generator.

You MUST obey these rules:
- Use ONLY the provided database schema.
- Only generate a single MySQL SELECT query.
- Do NOT modify data (no INSERT/UPDATE/DELETE/DDL).
- Do NOT use tables or columns that are not listed.
- Use backticks around identifiers when needed.
- Prefer simple, readable queries.

Database schema context:
{schema_context}

User question:
{user_question}

Return ONLY the SQL query, nothing else.
"""


sql_prompt = PromptTemplate(
    input_variables=["schema_context", "user_question"],
    template=SQL_PROMPT_TEMPLATE,
)


CORRECTION_PROMPT_TEMPLATE = """
You are an expert MySQL query fixer.

The following query failed:
SQL:
{sql_query}

Error:
{error_message}

Database schema:
{schema_context}

Generate a corrected MySQL SELECT query that:
- Fixes the error.
- Uses ONLY tables/columns from the schema.
- Does NOT modify data (no INSERT/UPDATE/DELETE/DDL).

Return ONLY the corrected SQL query.
"""


correction_prompt = PromptTemplate(
    input_variables=["sql_query", "error_message", "schema_context"],
    template=CORRECTION_PROMPT_TEMPLATE,
)

