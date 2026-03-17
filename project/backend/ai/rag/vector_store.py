from typing import List
import os

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from backend.config import settings


def _get_embeddings() -> OpenAIEmbeddings:
    """Return an embeddings instance configured for OpenAI."""
    return OpenAIEmbeddings(openai_api_key=settings.openai_api_key)


def get_vector_store() -> Chroma:
    """
    Get or create a Chroma vector store for schema documents.
    Uses a persistent directory so schema survives process restarts.
    """
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)
    return Chroma(
        collection_name="schema_collection",
        embedding_function=_get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def add_schema_documents(schema_texts: List[str], metadatas: List[dict]) -> None:
    """Add schema description documents to Chroma."""
    store = get_vector_store()
    store.add_texts(schema_texts, metadatas=metadatas)
    store.persist()


def retrieve_schema_relevant_to_question(question: str, k: int = 4) -> List[str]:
    """Retrieve top-k schema documents relevant to the user question."""
    store = get_vector_store()
    docs = store.similarity_search(question, k=k)
    return [d.page_content for d in docs]

