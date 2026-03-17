from dotenv import load_dotenv
import os

load_dotenv()

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # FastAPI
    app_name: str = "AI Database Generator and Conversational Data Analyst"
    api_prefix: str = "/api"

    # Database (MySQL)
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "hotels"

    # ⭐ Gemini LLM
    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    # ChromaDB
    chroma_persist_dir: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "chroma_store"
    )

    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:"
            f"{self.mysql_password}@{self.mysql_host}:"
            f"{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()