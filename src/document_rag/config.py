"""Environment-driven configuration. Never log secret settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_", env_file=".env", extra="ignore")

    api_key: SecretStr = Field(min_length=24)
    database_url: str = "postgresql+psycopg://rag:local-only-password@localhost:5432/rag"
    embedding_provider: Literal["local", "openai"] = "local"
    llm_provider: Literal["extractive", "openai"] = "extractive"
    openai_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    provider_timeout_seconds: float = Field(default=20, ge=1, le=120)
    max_upload_bytes: int = Field(default=5_000_000, ge=1024, le=25_000_000)
    max_pages: int = Field(default=60, ge=1, le=250)
    max_document_chars: int = Field(default=300_000, ge=1000, le=2_000_000)
    chunk_size: int = Field(default=900, ge=100, le=4000)
    chunk_overlap: int = Field(default=150, ge=0, le=1500)
    max_top_k: int = Field(default=10, ge=1, le=30)
    max_context_chars: int = Field(default=8000, ge=500, le=20000)
    min_vector_score: float = Field(default=0.10, ge=0, le=1)

    @model_validator(mode="after")
    def validate_pipeline(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        if self.embedding_provider == "openai" or self.llm_provider == "openai":
            if self.openai_api_key is None:
                raise ValueError("RAG_OPENAI_API_KEY required for an OpenAI provider")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
