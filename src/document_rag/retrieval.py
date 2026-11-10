"""Independent vector, full-text and reciprocal-rank-fusion retrieval."""

import re
from time import perf_counter

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from document_rag.config import Settings
from document_rag.models import Chunk, Document
from document_rag.providers import get_embedder
from document_rag.schemas import SearchHit, SearchRequest, SearchResponse

RRF_K = 60
MIN_TERM_COVERAGE = 0.70
# Query framing words are not evidence that the document supports an answer.
QUESTION_WORDS = frozenset(
    """
    a an and are as at be by can color could did do does each for from had
    has have how in is it its long many me much name of often on or our
    please tell than that the their there these this those time to use used
    was were what when where which who why will with would you your
    """.split()
)


def _stem(term: str) -> str:
    """Small deterministic lexical heuristic for offline demos, not linguistic stemming."""
    if len(term) >= 6:
        return term[:5]
    if len(term) > 3:
        return term.removesuffix("s")
    return term


def _keywords(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", text.casefold())
        if token not in QUESTION_WORDS and len(token) > 1
    ]


def _coverage(query: set[str], passage: str) -> float:
    if not query:
        return 0.0
    available = {_stem(token) for token in _keywords(passage)}
    return len(query & available) / len(query)


def _qualified_candidates(
    session: Session,
    statement,
    query_stems: set[str],
    target: int,
    min_vector_score: float | None = None,
):
    """Expand the SQL window until enough evidence passes filtering or rows end.

    Checking only the first `top_k * 6` unfiltered rows can cause false
    abstentions when higher-ranked chunks fail the lexical coverage test.
    A growing LIMIT scans farther without loading the entire corpus upfront.
    """
    window = max(target, 8)
    while True:
        rows = session.execute(statement.limit(window)).all()
        accepted = []
        for chunk, document, value in rows:
            if min_vector_score is not None:
                score = max(0.0, min(1.0, 1.0 - float(value)))
                if score < min_vector_score:
                    continue
            if _coverage(query_stems, chunk.content) < MIN_TERM_COVERAGE:
                continue
            accepted.append((chunk, document, value))
            if len(accepted) >= target:
                return accepted
        if len(rows) < window:
            return accepted
        window *= 2


def search(session: Session, request: SearchRequest, settings: Settings) -> SearchResponse:
    started = perf_counter()
    limit = min(request.top_k, settings.max_top_k)
    candidates = min(limit * 6, 60)
    by_id: dict[str, SearchHit] = {}
    rankings: list[list[str]] = []
    embedding_model = None
    keywords = _keywords(request.question)
    query_stems = {_stem(token) for token in keywords}
    if not query_stems:
        return SearchResponse(
            mode=request.mode,
            embedding_model=None,
            hits=[],
            retrieval_ms=round((perf_counter() - started) * 1000, 2),
        )

    def restrict(stmt):
        if request.document_ids is not None:
            return stmt.where(Document.id.in_(request.document_ids))
        return stmt

    if request.mode in ("vector", "hybrid"):
        embedder = get_embedder(settings)
        embedding_model = embedder.model_name
        query_vector = embedder.embed([request.question])[0]
        if any(query_vector):
            if request.document_ids is None:
                # HNSW applies embedding-model filters after the ANN scan. Iterative
                # scanning continues past the default candidate window as needed.
                # SET LOCAL is scoped to this transaction, not the pooled connection.
                session.execute(text("SET LOCAL hnsw.iterative_scan = strict_order"))
                distance = Chunk.embedding.cosine_distance(query_vector).label("distance")
                stmt = (
                    select(Chunk, Document, distance)
                    .join(Document, Chunk.document_id == Document.id)
                    .where(Chunk.embedding_model == embedder.model_name)
                    .order_by(distance)
                )
            else:
                # HNSW post-filtering can miss a rare document even with iterative
                # scans. Materialize the permitted document/model subset *before*
                # ranking: pgvector then computes exact distances within that subset.
                eligible = (
                    select(Chunk.id.label("chunk_id"), Chunk.embedding)
                    .where(
                        Chunk.document_id.in_(request.document_ids),
                        Chunk.embedding_model == embedder.model_name,
                    )
                    .cte("eligible_chunks")
                    .prefix_with("MATERIALIZED", dialect="postgresql")
                )
                distance = eligible.c.embedding.cosine_distance(query_vector).label("distance")
                stmt = (
                    select(Chunk, Document, distance)
                    .join(eligible, eligible.c.chunk_id == Chunk.id)
                    .join(Document, Chunk.document_id == Document.id)
                    .order_by(distance, Chunk.id)
                )
            ids = []
            for chunk, document, value in _qualified_candidates(
                session, stmt, query_stems, candidates, settings.min_vector_score
            ):
                score = max(0.0, min(1.0, 1.0 - float(value)))
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
        # Every term is escaped by the ASCII tokenizer; SQLAlchemy binds the tsquery parameter.
        query = func.to_tsquery("english", " | ".join(keywords))
        document_vector = func.to_tsvector("english", Chunk.content)
        rank = func.ts_rank(document_vector, query).label("rank")
        stmt = (
            select(Chunk, Document, rank)
            .join(Document, Chunk.document_id == Document.id)
            .where(document_vector.op("@@")(query))
            .order_by(rank.desc(), Chunk.id)
        )
        ids = []
        for chunk, document, value in _qualified_candidates(
            session, restrict(stmt), query_stems, candidates
        ):
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
