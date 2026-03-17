from langchain.prompts import PromptTemplate


SCHEMA_PROMPT_TEMPLATE = """
You are an expert MySQL database designer.

Task:
- From the following natural language description, design a single MySQL database.
- Focus on a clean, normalized schema but keep it simple and practical.
- Use snake_case table and column names.
- Prefer INT, FLOAT/DECIMAL, VARCHAR, DATE, DATETIME types.

Natural language request:
{user_request}

Number of rows to generate (hint for schema design, do NOT generate rows here):
{row_count}

Respond in strict JSON with the following structure and NOTHING else:
{{
  "database_name": "short_snake_case_name",
  "ddl_sql": "FULL_MYSQL_DDL_HERE",
  "tables": [
    {{
      "name": "table_name",
      "columns": [
        {{
          "name": "column_name",
          "type": "MYSQL_TYPE",
          "nullable": true,
          "is_primary_key": false,
          "references": "other_table.other_column | null"
        }}
      ]
    }}
  ]
}}
"""


schema_prompt = PromptTemplate(
    input_variables=["user_request", "row_count"],
    template=SCHEMA_PROMPT_TEMPLATE,
)

