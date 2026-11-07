# Document RAG Assistant

[![CI](https://github.com/RamonRDR/document-rag-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/RamonRDR/document-rag-assistant/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![License](https://img.shields.io/badge/License-MIT-green)

An inspectable **Retrieval-Augmented Generation** backend for PDF documents.
Built as an international software engineering portfolio project with FastAPI,
PostgreSQL, pgvector, PyMuPDF, hybrid retrieval, traceable citations, tests,
versioned migrations, a minimal local demo and deterministic evaluation.
No agent-orchestration framework is required.

## Features

- Bounded PDF ingestion: type/header validation, size/page/text limits,
  SHA-256 deduplication and error handling for corrupt, locked or textless PDFs.
- Page-preserving chunking with configurable overlap and embedding model version.
- PostgreSQL pgvector cosine-distance retrieval, full-text retrieval and
  Reciprocal Rank Fusion (RRF) to combine rankings.
- Independent POST /search endpoint for measuring retrieval separately from answers.
- Interchangeable local and OpenAI provider adapters. Context limits and
  an explicit abstention when no retrieved evidence is available.
- Source references constructed from actual database chunks, including PDF
  filename, page number, source ID and exact excerpt. Source references
  demonstrate provenance; they do not prove every model claim correct.
- Transactional reindexing from persisted page text and cascading deletion.
- Local-only HTML demo, API-key gate, Docker Compose, Alembic migrations.
- GitHub-hosted CI with real PostgreSQL/pgvector, fictional evaluation corpus,
  Ruff, API tests and Docker build. No paid API calls in CI.

## Architecture

PDF upload -> PyMuPDF -> extracted pages -> page-aware chunking -> embedding
adapter -> PostgreSQL + pgvector -> vector and/or keyword search -> RRF
-> bounded source context -> answer adapter -> answer with source metadata.

Raw PDF bytes are **not stored** after extraction. Extracted text, chunks and
vectors are stored until deletion. Ingestion is synchronous and bounded in
this MVP, not a background batch processor.

## Run locally

1. Install Docker Engine and Docker Compose.
2. Copy .env.example to .env.
3. Replace RAG_API_KEY with a fresh random secret at least 24 characters long.
4. Run: docker compose up --build
5. Visit http://localhost:8000 to upload a PDF and ask questions.
6. Inspect OpenAPI at http://localhost:8000/docs.

Compose binds API and database only to 127.0.0.1. The database password
shown in compose.yaml is **local development only**. Do not use this stack on
an internet-facing host without production auth, HTTPS, quotas and isolation.

### REST API

All document and query endpoints require header X-API-Key.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | /health | Liveness |
| POST | /documents | Multipart PDF upload and synchronous indexing |
| GET | /documents | List metadata |
| GET | /documents/{id} | Get metadata |
| DELETE | /documents/{id} | Delete document, pages and vectors |
| POST | /documents/{id}/reindex | Atomically rebuild embeddings |
| POST | /search | Independent retrieval and scores |
| POST | /ask | Answer with traceable citations or abstention |

Example: curl -X POST http://localhost:8000/search -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What is the policy?","mode":"hybrid","top_k":5}'

Search mode can be text, vector or hybrid, and document_ids optionally
restricts results. Scores are strategy-specific: cosine similarity,
PostgreSQL ts_rank and RRF are not interchangeable probabilities.

## Provider modes and real semantic RAG

Defaults are deliberately **offline and free**:

- RAG_EMBEDDING_PROVIDER=local provides normalized 1536-dimensional token
  hashing. This is **lexical matching, not semantic embeddings**.
- RAG_LLM_PROVIDER=extractive provides a clearly labeled quote preview,
  **not a generative LLM answer**.

For actual provider-backed semantic retrieval and LLM answers, explicitly
configure RAG_EMBEDDING_PROVIDER=openai, RAG_LLM_PROVIDER=openai and
RAG_OPENAI_API_KEY in your private .env file.

The configured OpenAI embedding defaults to text-embedding-3-small with 1536
dimensions; the chat model defaults to gpt-4o-mini. Changing dimensions
requires a database migration. Reindex documents after switching the
embedding provider. External calls transfer queries and document content to
the provider and may incur charges. Mandatory tests never make such calls.

## Development and evaluation

Install Python 3.14, PostgreSQL with pgvector, then:

    python -m pip install -e ".[dev]"
    ruff check .
    ruff format --check .
    alembic upgrade head
    pytest -q
    python -m document_rag.evaluation --output eval-report.json

Set RAG_DATABASE_URL and RAG_API_KEY in the environment. CI provisions the
database independently and uses no self-hosted runner.

The evaluation uses 25 entirely fictional questions (20 answerable and
5 unanswerable), real PostgreSQL retrieval, two chunk/overlap configurations
and three search modes. It reports Recall@K, Precision@K, MRR@K, average
retrieval time and no-result rates for unsupported questions. Its transaction
is rolled back so evaluation content is not committed. It does **not**
measure semantic-model quality, generated-answer correctness, grounding
faithfulness, token billing or provider latency. No benchmark numbers are
fabricated.

See [architecture](docs/architecture.md) and [security](docs/security.md).

## Merge and deployment policy

The GitHub Actions pipeline runs on PR updates to main and manual dispatch.
It never automatically deploys or merges. Main-branch merge requires human
approval and final technical review. MIT licensed, copyright 2026 Ramon Rodriguez.
