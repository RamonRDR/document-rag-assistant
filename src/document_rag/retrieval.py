"""Independent vector, full-text and reciprocal-rank-fusion retrieval."""

from time import perf_counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from document_rag.config import Settings
from document_rag.models import Chunk, Document
from document_rag.providers import get_embedder
from document_rag.schemas import SearchHit, SearchRequest, SearchResponse

RRF_K = 60


def search(session: Session, request: SearchRequest, settings: Settings) -> SearchResponse:
    started = perf_counter()
    limit = min(request.top_k, settings.max_top_k)
    candidates = min(limit * 3, 30)
    by_id: dict[str, SearchHit] = {}
    rankings: list[list[str]] = []
    embedding_model = None

    def restrict(stmt):
        if request.document_ids is not None:
            return stmt.where(Document.id.in_(request.document_ids))
        return stmt

    if request.mode in ("vector", "hybrid"):
        embedder = get_embedder(settings)
        embedding_model = embedder.model_name
        query_vector = embedder.embed([request.question])[0]
        if any(query_vector):
            distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
            stmt = (
                select(Chunk, Document, distance)
                .join(Document, Chunk.document_id == Document.id)
                .where(Chunk.embedding_model == embedder.model_name)
                .order_by(distance)
                .limit(candidates)
            )
            ids = []
            for chunk, document, value in session.execute(restrict(stmt)):
                score = max(0.0, min(1.0, 1.0 - float(value)))
                if score < settings.min_vector_score:
                    continue
                ids.append(chunk.id)
                by_id[chunk.id] = SearchHit(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    filename=document.filename,
                    page=chunk.page,
                    text=chunk.content,
                    score=score,
                )
            rankings.append(ids)

    if request.mode in ("text", "hybrid"):
        query = func.plainto_tsquery("simple", request.question)
        document_vector = func.to_tsvector("simple", Chunk.content)
        rank = func.ts_rank(document_vector, query).label("rank")
        stmt = (
            select(Chunk, Document, rank)
            .join(Document, Chunk.document_id == Document.id)
            .where(document_vector.op("@@")(query))
            .order_by(rank.desc())
            .limit(candidates)
        )
        ids = []
        for chunk, document, value in session.execute(restrict(stmt)):
            ids.append(chunk.id)
            if chunk.id not in by_id:
                by_id[chunk.id] = SearchHit(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    filename=document.filename,
                    page=chunk.page,
                    text=chunk.content,
                    score=float(value),
                )
        rankings.append(ids)

    if request.mode == "hybrid":
        fused = {}
        for ranked in rankings:
            for index, chunk_id in enumerate(ranked):
                fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (RRF_K + index + 1)
        ordered = sorted(fused, key=lambda chunk_id: (-fused[chunk_id], chunk_id))
        hits = [
            by_id[chunk_id].model_copy(update={"score": fused[chunk_id]})
            for chunk_id in ordered[:limit]
        ]
    else:
        hits = sorted(by_id.values(), key=lambda hit: (-hit.score, hit.chunk_id))[:limit]
    return SearchResponse(
        mode=request.mode,
        embedding_model=embedding_model,
        hits=hits,
        retrieval_ms=round((perf_counter() - started) * 1000, 2),
    )
