"""Public API contracts. Source IDs are always resolved from persisted chunks."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    sha256: str
    byte_size: int
    page_count: int
    status: str
    created_at: datetime


class SearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    mode: Literal["vector", "text", "hybrid"] = "hybrid"
    top_k: int = Field(default=5, ge=1, le=30)
    document_ids: list[str] | None = Field(default=None, max_length=30)


class SearchHit(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page: int
    text: str
    score: float


class SearchResponse(BaseModel):
    mode: str
    embedding_model: str | None
    hits: list[SearchHit]
    retrieval_ms: float


class Citation(BaseModel):
    source_id: str
    chunk_id: str
    document_id: str
    filename: str
    page: int
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    mode: str
    model: str
    retrieval_ms: float
    generation_ms: float
    tokens_used: int | None = None
