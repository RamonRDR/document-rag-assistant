"""Transactional indexing with page provenance and replace-on-reindex."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from document_rag.chunking import PageText, chunk_pages
from document_rag.config import Settings
from document_rag.ingest import ExtractedPDF
from document_rag.models import Chunk, Document, Page
from document_rag.providers import get_embedder


def index_pages(
    session: Session, document: Document, pages: list[PageText], settings: Settings
) -> int:
    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)
    embedder = get_embedder(settings)
    # External calls happen before deleting the old index, so failed calls cannot destroy it.
    batch_size = 32
    vectors: list[list[float]] = []
    for offset in range(0, len(chunks), batch_size):
        vectors.extend(embedder.embed([part.text for part in chunks[offset : offset + batch_size]]))
    session.execute(delete(Chunk).where(Chunk.document_id == document.id))
    session.flush()
    for part, vector in zip(chunks, vectors, strict=True):
        session.add(
            Chunk(
                document_id=document.id,
                page=part.page,
                ordinal=part.ordinal,
                content=part.text,
                embedding_model=embedder.model_name,
                embedding=vector,
            )
        )
    document.status = "ready"
    return len(chunks)


def persist_pdf(
    session: Session, extracted: ExtractedPDF, filename: str, settings: Settings
) -> Document:
    document = Document(
        filename=filename,
        sha256=extracted.sha256,
        byte_size=extracted.byte_size,
        page_count=extracted.page_count,
        status="indexing",
    )
    session.add(document)
    session.flush()
    session.add_all(
        [
            Page(document_id=document.id, number=page.number, content=page.text)
            for page in extracted.pages
        ]
    )
    index_pages(session, document, extracted.pages, settings)
    return document


def reindex(session: Session, document: Document, settings: Settings) -> int:
    rows = session.scalars(
        select(Page).where(Page.document_id == document.id).order_by(Page.number)
    ).all()
    pages = [PageText(number=row.number, text=row.content) for row in rows]
    if not pages:
        raise ValueError("No persisted text pages to reindex")
    return index_pages(session, document, pages, settings)
