"""Reproducible, transaction-rolled-back retrieval evaluation against real PostgreSQL."""
import argparse
import hashlib
import json
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from document_rag.chunking import PageText
from document_rag.config import get_settings
from document_rag.indexing import index_pages
from document_rag.models import Document, Page
from document_rag.retrieval import search
from document_rag.schemas import SearchRequest


def summarize(rows: list[dict], k: int) -> dict[str, float | int]:
    positive = [row for row in rows if row["expected"] is not None]
    negative = [row for row in rows if row["expected"] is None]
    recall = sum(row["expected"] in row["retrieved"][:k] for row in positive)
    precision = sum(
        sum(doc == row["expected"] for doc in row["retrieved"][:k]) / k for row in positive
    )
    ranks = [
        next(
            (1.0 / (index + 1) for index, doc in enumerate(row["retrieved"][:k])
             if doc == row["expected"]),
            0.0,
        )
        for row in positive
    ]
    return {
        "positive_cases": len(positive),
        "unanswerable_cases": len(negative),
        "recall_at_k": round(recall / len(positive), 4) if positive else 0.0,
        "precision_at_k": round(precision / len(positive), 4) if positive else 0.0,
        "mrr_at_k": round(sum(ranks) / len(positive), 4) if positive else 0.0,
        "no_result_rate_for_unanswerable": (
            round(sum(not row["retrieved"][:k] for row in negative) / len(negative), 4)
            if negative else 0.0
        ),
    }


def evaluate(data_path: Path) -> dict:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if not 20 <= len(data["cases"]) <= 30:
        raise ValueError("Evaluation suite must contain 20 to 30 questions")
    settings = get_settings().model_copy(
        update={"embedding_provider": "local", "llm_provider": "extractive"}
    )
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    report = {
        "type": "real PostgreSQL retrieval with deterministic local lexical embeddings",
        "paid_llm": False,
        "limitations": (
            "No generative answer correctness or semantic model performance is measured. "
            "This corpus contains fictional documents, with document-level relevance labels."
        ),
        "questions": len(data["cases"]),
        "runs": [],
    }
    try:
        with Session(engine) as session:
            ids = {}
            for record in data["documents"]:
                content = record["text"]
                document = Document(
                    filename=record["filename"],
                    sha256=hashlib.sha256(content.encode()).hexdigest(),
                    byte_size=len(content.encode()),
                    page_count=1,
                    status="ready",
                )
                session.add(document)
                session.flush()
                session.add(Page(document_id=document.id, number=1, content=content))
                ids[record["id"]] = document
            session.flush()
            for chunk_size, overlap in ((320, 40), (900, 150)):
                trial = settings.model_copy(update={"chunk_size": chunk_size, "chunk_overlap": overlap})
                for record in data["documents"]:
                    index_pages(
                        session,
                        ids[record["id"]],
                        [PageText(number=1, text=record["text"])],
                        trial,
                    )
                session.flush()
                for mode in ("vector", "text", "hybrid"):
                    rows = []
                    for case in data["cases"]:
                        result = search(
                            session,
                            SearchRequest(
                                question=case["question"],
                                mode=mode,
                                top_k=5,
                                document_ids=[item.id for item in ids.values()],
                            ),
                            trial,
                        )
                        inverse = {document.id: key for key, document in ids.items()}
                        rows.append({
                            "expected": case["expected"],
                            "retrieved": [inverse[hit.document_id] for hit in result.hits],
                            "retrieval_ms": result.retrieval_ms,
                        })
                    report["runs"].append({
                        "chunk_size": chunk_size,
                        "overlap": overlap,
                        "mode": mode,
                        "metrics": {str(k): summarize(rows, k) for k in (1, 3, 5)},
                        "mean_retrieval_ms": round(
                            sum(row["retrieval_ms"] for row in rows) / len(rows), 2
                        ),
                    })
            session.rollback()  # No fixture content is committed to the user's database.
    finally:
        engine.dispose()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval using fictional data")
    parser.add_argument("--data", default="evaluation/fixtures.json")
    parser.add_argument("--output", default="evaluation-results.json")
    args = parser.parse_args()
    report = evaluate(Path(args.data))
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
