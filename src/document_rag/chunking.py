"""Deterministic, page-aware character chunker with bounded overlap."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PageText:
    number: int
    text: str


@dataclass(frozen=True)
class TextChunk:
    page: int
    ordinal: int
    text: str


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_pages(pages: list[PageText], size: int, overlap: int) -> list[TextChunk]:
    if size < 1 or overlap < 0 or overlap >= size:
        raise ValueError("chunk size must exceed overlap")
    chunks: list[TextChunk] = []
    for page in pages:
        clean = normalize(page.text)
        step = size - overlap
        for start in range(0, len(clean), step):
            piece = clean[start : start + size].strip()
            if piece:
                chunks.append(TextChunk(page=page.number, ordinal=len(chunks), text=piece))
            if start + size >= len(clean):
                break
    return chunks
