from typing import List

from backend.ai.rag.vector_store import retrieve_schema_relevant_to_question
from backend.database.schema_manager import DatabaseSchema


def schema_to_documents(schema: DatabaseSchema) -> List[str]:
    """
    Convert a DatabaseSchema object into descriptive text chunks
    suitable for vector search.
    """
    docs: List[str] = []
    for table in schema.tables:
        lines = [f"Table {table.name}:"]
        for col in table.columns:
            col_desc = f"- {col.name} {col.type}"
            if col.is_primary_key:
                col_desc += " PRIMARY KEY"
            if col.references:
                col_desc += f" REFERENCES {col.references}"
            lines.append(col_desc)
        docs.append("\n".join(lines))
    return docs


def get_relevant_schema_text(question: str, k: int = 4) -> str:
    """
    Retrieve schema snippets relevant to a user question and
    return them as a single concatenated context string.
    """
    docs = retrieve_schema_relevant_to_question(question, k=k)
    return "\n\n".join(docs)

