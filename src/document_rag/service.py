"""RAG composition: bounded context, deterministic source IDs and abstention."""
from time import perf_counter

from sqlalchemy.orm import Session

from document_rag.config import Settings
from document_rag.providers import get_answerer
from document_rag.retrieval import search
from document_rag.schemas import AskResponse, Citation, SearchRequest

NO_EVIDENCE = "I could not find enough evidence in the indexed documents to answer."


def answer_question(session: Session, request: SearchRequest, settings: Settings) -> AskResponse:
    results = search(session, request, settings)
    answerer = get_answerer(settings)
    if not results.hits:
        return AskResponse(
            answer=NO_EVIDENCE,
            citations=[],
            mode=request.mode,
            model="none",
            retrieval_ms=results.retrieval_ms,
            generation_ms=0.0,
        )

    citations: list[Citation] = []
    segments = []
    used = 0
    for hit in results.hits:
        header = f"SOURCE {len(citations) + 1} | {hit.filename} | PAGE {hit.page} | CONTENT:\n"
        remaining = settings.max_context_chars - used - len(header)
        if remaining < 100:
            break
        excerpt = hit.text[:remaining]
        citations.append(
            Citation(
                source_id=f"S{len(citations) + 1}",
                chunk_id=hit.chunk_id,
                document_id=hit.document_id,
                filename=hit.filename,
                page=hit.page,
                excerpt=excerpt,
            )
        )
        segments.append(header + excerpt)
        used += len(header) + len(excerpt)
    if not citations:
        return AskResponse(
            answer=NO_EVIDENCE,
            citations=[],
            mode=request.mode,
            model="none",
            retrieval_ms=results.retrieval_ms,
            generation_ms=0.0,
        )

    started = perf_counter()
    generated = answerer.generate(request.question, "\n\n".join(segments))
    return AskResponse(
        answer=generated.text,
        citations=citations,
        mode=request.mode,
        model=generated.model,
        retrieval_ms=results.retrieval_ms,
        generation_ms=round((perf_counter() - started) * 1000, 2),
        tokens_used=generated.tokens,
    )
