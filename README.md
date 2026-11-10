<div align="center">

# Document RAG Assistant 📚

**Chat with your PDFs. Inspect every source. Keep retrieval accountable.**

[🇺🇸 English](README.md) · [🇧🇷 Português](README.pt-BR.md) · [🇪🇸 Español](README.es.md)

[![CI](https://github.com/RamonRDR/document-rag-assistant/actions/workflows/ci.yml/badge.svg?event=pull_request)](https://github.com/RamonRDR/document-rag-assistant/actions/workflows/ci.yml)
![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB)
![License MIT](https://img.shields.io/badge/License-MIT-22A06B)

![FastAPI >=0.115](https://img.shields.io/badge/FastAPI-%3E%3D0.115-009688)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063)
![Pydantic Settings](https://img.shields.io/badge/Pydantic-Settings-B72867)
![SQLAlchemy 2](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00)
![psycopg 3](https://img.shields.io/badge/psycopg-3-4169E1)
![Uvicorn ASGI](https://img.shields.io/badge/Uvicorn-ASGI-4051B5)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF%20extraction-1864AB)
![python-multipart](https://img.shields.io/badge/python-multipart%20uploads-4C7E9C)
![httpx](https://img.shields.io/badge/httpx-test%20transport-5755D9)

![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-336791)
![pgvector 1536d](https://img.shields.io/badge/pgvector-1536d%20vectors-4877B8)
![Alembic migrations](https://img.shields.io/badge/Alembic-migrations-555555)
![Docker](https://img.shields.io/badge/Docker-image%20build-2496ED)
![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED)
![Hatchling](https://img.shields.io/badge/Hatchling-build%20backend-4B5563)

![RAG](https://img.shields.io/badge/RAG-retrieval%20pipeline-4C51BF)
![Hybrid RRF](https://img.shields.io/badge/Hybrid%20search-RRF-6A5ACD)
![PostgreSQL FTS](https://img.shields.io/badge/PostgreSQL-full%20text%20search-336791)
![Local embeddings](https://img.shields.io/badge/Embeddings-local%20lexical-8661C1)
![OpenAI optional](https://img.shields.io/badge/OpenAI%20adapter-optional%20unverified-8D6A37)
![Traceable citations](https://img.shields.io/badge/Citations-document%20%2B%20page-438887)

![pytest 29 passing](https://img.shields.io/badge/pytest-29%20passing-0A9EDC)
![Ruff lint & format](https://img.shields.io/badge/Ruff-lint%20%26%20format-8D9D1C)
![DB integration tests](https://img.shields.io/badge/PostgreSQL-integration%20tested-4A8D6A)
![RAG evaluation 25](https://img.shields.io/badge/RAG%20eval-25%20fictitious%20questions-795F8B)
![Docker build CI](https://img.shields.io/badge/Docker%20build-CI%20verified-276A9D)
![OpenAPI](https://img.shields.io/badge/OpenAPI-Swagger%20UI-6BA539)

</div>

> **Project status:** Implemented on [PR #1](https://github.com/RamonRDR/document-rag-assistant/pull/1), currently **not merged** into `main`. The last pre-documentation GitHub Actions [run #6](https://github.com/RamonRDR/document-rag-assistant/actions/runs/42419199438) passed 29 automated tests, Ruff, Alembic, PostgreSQL/pgvector integration, retrieval evaluation and Docker build. The final Codex review is **pending owner authorization**. Nothing has been deployed.

## Overview

An inspectable, source-traceable PDF question-answering API and local demo built for an international Python/backend and applied-AI engineering portfolio. It emphasizes the **retrieval pipeline** over a chat wrapper: PDF extraction, original page references, chunking, indexed vectors, text search, rank fusion, provenance and deterministic evaluation.

**Audience:** international recruiters and engineers reviewing Python, API, data persistence and RAG implementations. This English file is canonical; the Portuguese and Spanish READMEs cover the same functionality, setup and limitations.

## Implemented features

- Validated PDF upload with file-extension, MIME/header, byte, page and text limits; explicit errors for corrupted, password-protected and non-text PDFs.
- SHA-256 deduplication of **identical PDF bytes**, unique document IDs, metadata listing, lookup and deletion. PDFs regenerated from identical text may have different hashes.
- Page-aware normalization, configurable chunk length and overlap, stored page numbers and model identifiers, 1536-dimensional vectors.
- PostgreSQL storage with pgvector cosine-distance retrieval, English full-text search and hybrid **Reciprocal Rank Fusion (RRF)** with deduplication and conservative lexical evidence filtering.
- Separate `POST /search` endpoint with strategy-specific scores and `POST /ask` endpoint that returns an answer or abstains with traceable source excerpts.
- A deterministic local lexical embedding baseline and extractive answer preview; an **optional, unverified OpenAI integration** via replaceable adapters.
- Transactional reindexing from stored page text, cascading deletion of chunks and embeddings, API-key gated document/query endpoints.
- Minimal browser demo, OpenAPI/Swagger UI, Docker Compose and GitHub-hosted testing with **no paid API calls**.

## Technology stack

| Layer | Verified technology and version/capability |
| --- | --- |
| Language/runtime | Python **3.14** in Docker and CI; project requires Python `>=3.14` |
| API and validation | FastAPI `>=0.115,<1`; Pydantic **v2**, Pydantic Settings, Uvicorn ASGI, python-multipart |
| Database | PostgreSQL **17** via `pgvector/pgvector:pg17`; SQLAlchemy **2.x**, psycopg **3**, pgvector, Alembic |
| PDF | PyMuPDF (declared minimum `1.26.6`) |
| RAG | 1536d local token-hash baseline, pgvector cosine search, PostgreSQL English FTS, RRF, structured citations |
| Optional provider | OpenAI Python SDK and provider adapters (declared; external-provider integration **not exercised** in CI) |
| Testing/build | pytest, httpx-backed FastAPI TestClient, Ruff, Hatchling packaging, Docker image and Docker Compose |
| Automation | GitHub Actions hosted runners; Alembic migrations, unit/API/DB tests, fictional retrieval evaluation, Docker build |

Dependency numbers containing `>=` are **declared minimums**, not claims about exact resolved patch versions. `pytest-cov` is installed as a dev dependency but the workflow **does not measure coverage**. There is **no mypy check** in CI.

## Architecture

```text
PDF upload → PyMuPDF → extracted pages → page-aware chunks
                                            ↓
                                   embedding adapter
                                            ↓
                              PostgreSQL + pgvector
                                            ↓
Question → vector search / English FTS → RRF + evidence filter
                                            ↓
                              bounded source context
                                            ↓
                         extractive or optional LLM adapter
                                            ↓
                         answer + document/page citations
```

Three persisted tables hold documents, extracted pages and chunks with source metadata. Raw PDF bytes are **discarded** after extraction; extracted text and embeddings remain until deletion. Reindexing rebuilds from page text and commits atomically. Retrieved content is treated as untrusted data, never executable commands.

For deeper implementation details, consult [architecture](docs/architecture.md) and [security](docs/security.md).

## Prerequisites

- Recommended: Docker Engine with Docker Compose, free ports **8000** and **5432** on localhost.
- Alternatively: Python **3.14**, PostgreSQL **17** with the `vector` extension, and a local Python virtual environment.
- A fresh secret for `RAG_API_KEY` with at least **24 characters**. The default local operation requires **no OpenAI key**.

## Install and run with Docker Compose

```bash
cp .env.example .env
# Replace RAG_API_KEY in .env with a unique random secret, 24+ characters.
docker compose up --build
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead of `cp` if needed. Compose starts a database health check, applies `alembic upgrade head`, and starts Uvicorn.

- Demo: http://localhost:8000/
- Interactive API docs: http://localhost:8000/docs
- OpenAPI specification: http://localhost:8000/openapi.json
- Liveness: http://localhost:8000/health

Compose binds the API and database to `127.0.0.1`. Its example database password `local-only-password` is **for local development only**. Do not expose this stack to the internet.

## Configuration

The file [.env.example](.env.example) lists the primary variables. All application options use the `RAG_` prefix.

| Variable | Default/meaning |
| --- | --- |
| `RAG_API_KEY` | **Required**, a private secret of at least 24 characters |
| `RAG_DATABASE_URL` | PostgreSQL connection string; Compose overrides the host with `db` |
| `RAG_EMBEDDING_PROVIDER` | `local` or `openai`; defaults to `local` |
| `RAG_LLM_PROVIDER` | `extractive` or `openai`; defaults to `extractive` |
| `RAG_OPENAI_API_KEY` | Required **only when an OpenAI provider is selected** |
| `RAG_OPENAI_EMBEDDING_MODEL` | Defaults to `text-embedding-3-small`, expecting 1536 dimensions |
| `RAG_OPENAI_CHAT_MODEL` | Defaults to `gpt-4o-mini` |
| `RAG_MAX_UPLOAD_BYTES` / `RAG_MAX_PAGES` | Defaults to **5,000,000 bytes / 60 pages** |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | Defaults to **900 / 150** characters |
| `RAG_MAX_TOP_K` / `RAG_MAX_CONTEXT_CHARS` | Defaults to **10 / 8000** |
| `RAG_MIN_VECTOR_SCORE` | Defaults to **0.10**; not a calibrated confidence guarantee |

Do not commit `.env`, provider secrets or confidential PDFs.

## Local Python installation

Start PostgreSQL with pgvector, set `RAG_DATABASE_URL` and `RAG_API_KEY`, then run:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
alembic upgrade head
uvicorn document_rag.api:app --reload
```

Windows PowerShell virtual-environment activation: `.venv\Scripts\Activate.ps1`. Use a dedicated disposable test database for experimentation.

## Use the demo and API

In the local demo, enter `RAG_API_KEY`, select a PDF, upload it, then ask questions. You can inspect retrieved chunks separately, change the retrieval strategy and see source filename/page and snippets. The interface keeps the key in the current tab's memory and is **not designed for public hosting**.

**Upload (201):**

```bash
curl -X POST http://localhost:8000/documents -H "X-API-Key: YOUR_KEY" -F "file=@sample.pdf"
```

**Retrieve supporting excerpts:**

```bash
curl -X POST http://localhost:8000/search -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What does the document say about the policy?","mode":"hybrid","top_k":5}'
```

**Answer with citations:**

```bash
curl -X POST http://localhost:8000/ask -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What does the document say about the policy?","mode":"hybrid","top_k":5}'
```

These are request examples, **not evidence of model answer accuracy**. Response objects include chunk and document IDs, filename, original page, excerpts, timing and, when available, provider token count.

## REST API reference

All routes below except the demo, liveness and OpenAPI/Swagger UI require `X-API-Key`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness, **not** database readiness |
| GET | `/` | Local HTML demo |
| POST | `/documents` | Upload and synchronously index PDF |
| GET | `/documents` | List up to 200 document metadata records |
| GET | `/documents/{document_id}` | Get document metadata |
| DELETE | `/documents/{document_id}` | Delete document, extracted pages and vectors |
| POST | `/documents/{document_id}/reindex` | Transactionally rebuild embeddings |
| POST | `/search` | Return text, vector or hybrid results and scores |
| POST | `/ask` | Answer, citations or explicit no-evidence result |
| GET | `/docs` / `/openapi.json` | Swagger UI / OpenAPI schema |

`mode` is one of `text`, `vector` or `hybrid`, and `document_ids` may restrict search scope. Cosine similarity, `ts_rank` and RRF scores have **different scales**.

## Provider modes and quality evaluation

The default `local` embedder is deterministic normalized token hashing, **not a semantic model**. The default `extractive` answerer shows an excerpt preview, **not an LLM-generated answer**. OpenAI adapters are implemented but real paid API calls, answer faithfulness and provider latencies **have not been validated**.

The evaluation corpus contains **25 fictional questions (20 answerable, 5 unsupported)** and compares two chunk/overlap configurations and three retrieval strategies in a PostgreSQL transaction that is rolled back. Its metrics are Recall@K, Precision@K, MRR@K, retrieval timing and unsupported-question no-result rate. In the CI [run #6](https://github.com/RamonRDR/document-rag-assistant/actions/runs/42419199438), lexical-baseline Recall@1 was **95% vector, 100% text and 100% hybrid**, with all five unsupported questions returning no matches in this small synthetic corpus. These findings do **not** establish general semantic accuracy, grounded generation or injection resistance.

## Automated tests, CI and badge maintenance

```bash
ruff check .
ruff format --check .
alembic upgrade head
pytest -q
python -m document_rag.evaluation --output eval-report.json
docker build -t document-rag-assistant:local .
```

The GitHub Actions [CI workflow](.github/workflows/ci.yml) runs on pull requests to `main` and manual dispatch. It uses Python 3.14 and an ephemeral pgvector/PostgreSQL 17 service with fictional data; its gates include Ruff lint/format, migration, unit and integration tests, deterministic evaluation and Docker image build. It performs **no automatic merge, deploy, live LLM call or self-hosted execution**.

**Badge provenance:** `pytest | 29 passing` is a static snapshot verified by [CI run #6](https://github.com/RamonRDR/document-rag-assistant/actions/runs/42419199438), not an automatically refreshing test count. A lightweight CI verification checks all three README badges against the real pytest JUnit result. When the test suite changes, update all three counts in the same PR. The CI status image is dynamic and tracks pull-request runs of this repository's workflow (the feature branch is not yet merged into main). No coverage or type-check pass badge is shown because those checks are not executed.

## Security and privacy

Document and query routes use a minimum-length API secret compared in constant time. Upload constraints reject malformed, oversized, locked and image-only PDFs; retrieved contents are displayed as text, not executable HTML. The service does not execute PDF scripts or embedded commands. The OpenAI adapter can transmit document-derived context and questions externally **only when explicitly configured**, with possible charges and privacy implications.

This is a **single-operator local demonstration**, not a hardened multi-tenant or public SaaS. It lacks per-user document authorization, rate limits, request limits at an ingress proxy, parser sandboxing, file scanning, audit infrastructure and production secret handling. Deletion removes active database rows, not necessarily external backups. See [security notes](docs/security.md).

## Known limitations

- No OCR, queued ingestion, progress dashboard or token streaming; large documents are deliberately bounded.
- No production auth, tenant isolation, HTTPS termination or deployment configuration.
- PDF parsing can still have native-library vulnerabilities; prompting alone does not guarantee protection against prompt injection.
- Source citations are generated from retrieved chunks but do not prove every generated statement is correct.
- OpenAI integration is optional and **not verified in CI**. No real-world quality or paid-token/cost benchmarks are claimed.
- The project is on a PR and awaits the authorized final Codex review before a potential merge.

## Repository structure

| Path | Responsibility |
| --- | --- |
| `src/document_rag/api.py` | FastAPI routes, API key, OpenAPI |
| `src/document_rag/ingest.py` | PDF validation and PyMuPDF extraction |
| `src/document_rag/chunking.py` | Page-aware chunk creation |
| `src/document_rag/indexing.py` | Transactional ingestion and reindexing |
| `src/document_rag/retrieval.py` | pgvector, English FTS and RRF |
| `src/document_rag/providers.py` | Local/OpenAI provider adapters |
| `src/document_rag/service.py` | Bounded context and sourced answers |
| `src/document_rag/models.py` / `db.py` | SQLAlchemy schema and sessions |
| `src/document_rag/evaluation.py` / `evaluation/` | Synthetic retrieval evaluation |
| `src/document_rag/ui.py` | Single-page local browser demo |
| `migrations/` | Alembic schema migration |
| `tests/` | Unit and PostgreSQL integration tests |
| `.github/workflows/ci.yml` | Hosted CI quality gates |
| `scripts/` | README badge/test-count consistency check |
| `docs/` | Architecture and security decisions |

## Possible future improvements

With separate scope and explicit validation: OCR, asynchronous indexing, document-level authorization, hardened public demo, streaming, semantic model benchmarking and groundedness evaluations. None of these are advertised as currently delivered.

## Contributing and review

Propose focused changes with tests and documentation in a feature branch. Keep all fixtures fictional and all external paid providers disabled in mandatory CI. This PR requires an authorized Codex review and explicit owner approval before merge.

## License

[MIT License](LICENSE), copyright © 2026 Ramon Rodriguez.
