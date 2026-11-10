# Architecture and engineering decisions

## Document lifecycle

The documents table stores metadata and unique SHA-256. The pages table stores
extracted text and original 1-based page number; raw PDFs are discarded.
The chunks table stores text, document ID, page, ordinal, embedding model
identifier and a 1536-dimensional vector. PostgreSQL cascading deletes remove
pages and vectors. Reindex generates all new embeddings before replacing
old chunks in one transaction. Failures leave the previous index intact.

## Retrieval and ranking

For vector requests without a document scope, retrieval sorts by pgvector cosine
distance using the HNSW index with transaction-local
`hnsw.iterative_scan = strict_order`. This expands the index scan when
embedding-model post-filtering discards nearer chunks, subject to pgvector's
scan limits. When `document_ids` is specified, the application instead uses a
PostgreSQL `MATERIALIZED` CTE to filter by document IDs and embedding model
*before* exact cosine ranking. This intentionally trades speed for predictable
scoped recall, avoiding HNSW's post-filtering problem entirely. Neither strategy
guarantees semantic relevance: a separate lexical evidence filter still applies.
Keyword retrieval uses PostgreSQL English full-text search with OR candidate matching
and an expression GIN index. An explicit, conservative lexical term-coverage
filter removes weak evidence in both keyword and vector modes. The filter
uses a simple token-prefix heuristic, not linguistic or semantic entailment;
it can reject valid paraphrases and cannot guarantee answer faithfulness. Common
question framing such as "tell me about" is excluded from the evidence
requirement, while queries with only framing terms still abstain. Vector
and full-text retrieval expand the SQL candidate window geometrically until
sufficient chunks pass this evidence filter or the available ranking is exhausted,
so rejected high-ranked rows cannot consume a fixed candidate budget. This can
increase database work on weak or unsupported queries. For unscoped HNSW,
results remain approximate and subject to pgvector scan limits. Hybrid retrieval
fuses two ranked candidate lists
with reciprocal rank fusion (RRF, k=60). It deduplicates by chunk ID and
preserves document/page metadata. The three scoring scales differ; higher
hybrid scores do not imply calibrated probabilities.

Vector search filters by embedding model identifier so vectors indexed
with incompatible providers are not silently mixed. Reindex existing
documents after changing provider. The local embedding mode is a deterministic
**lexical test baseline**. OpenAI embeddings are optional for semantic search.

## Grounded answering

The search stage is exposed independently at POST /search. The answer stage
at POST /ask sends only retrieved source excerpts up to the configured context
limit to the selected answer adapter. Source citations are created by the
server from retrieved chunk data; the provider never supplies document IDs
or page numbers. The grounded-v1 system prompt treats retrieved text as
untrusted data. Prompt injection is not solved by prompting alone.

## Explicit tradeoffs

A bounded synchronous ingest route is practical for a small demo but lacks
a queue, progress tracking and file scanning. The app is single-operator
local software, not multi-tenant or publicly deployable as supplied. It does
not implement OCR or genuine token streaming. The evaluation measures local
lexical retrieval, not LLM grounding. A production evolution would add a
worker queue, task state, stronger auth/ACLs, document quotas, safe PDF
sandboxing, observability and human-rated semantic evaluation.
