"""Evaluation suite tests only definitions and deterministic metrics."""

import json
from pathlib import Path

from document_rag.evaluation import summarize


def test_fixture_has_25_labeled_questions_and_no_real_personal_data():
    data = json.loads(Path("evaluation/fixtures.json").read_text(encoding="utf-8"))
    assert len(data["cases"]) == 25
    assert len(data["documents"]) == 5
    assert sum(case["expected"] is None for case in data["cases"]) == 5
    ids = {doc["id"] for doc in data["documents"]}
    assert all(case["expected"] is None or case["expected"] in ids for case in data["cases"])


def test_reciprocal_rank_metrics():
    rows = [
        {"expected": "doc-a", "retrieved": ["doc-b", "doc-a"]},
        {"expected": "doc-b", "retrieved": ["doc-b"]},
    ]
    scores = summarize(rows, 3)
    assert scores["recall_at_k"] == 1
    assert scores["mrr_at_k"] == 0.75
