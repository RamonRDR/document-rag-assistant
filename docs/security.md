# Security and privacy

Implemented:
- API-key validation with constant-time comparison on all document and query
  endpoints. Public routes expose only docs, a blank demo UI and liveness.
- File extension, MIME/header and byte size validation, page/text limits,
  explicit rejection of corrupt, locked and image-only PDFs.
- Server-side SQLAlchemy parameterization; HTML demo renders untrusted content
  with textContent, not innerHTML.
- No execution of document scripts or commands. Prompt instructions tell the
  LLM to treat retrieved content as untrusted data, but this does **not**
  guarantee immunity to prompt injection or unsupported generated claims.
- No external provider calls by default. Provider API credentials are loaded
  from environment variables. No paid calls in mandatory CI.
- Cascading deletion of stored page text, chunks and embeddings. External
  backups/replicas can have separate retention policies.

Known limitations:
- This is a **local single-operator demonstration**, not an internet-facing
  system. Anyone possessing the single API key can read any indexed file.
- Docker Compose uses an intentionally obvious local-only database password.
  Change it and implement full authorization, TLS, rate limiting, quotas,
  auditing and credential rotation before exposing a deployment.
- Native PDF parsers have attack surface even without executing embedded
  scripts. Production parsing should be sandboxed, patched and scanned.
- Ingress request-size restrictions are recommended because the web framework
  may spool uploads before application validation.
- OpenAI mode explicitly transmits document-derived snippets and questions
  to an external provider. Review privacy, residency, billing and consent
  before enabling it for non-fictitious documents.
- Evaluation fixtures contain only fictional records. Do not index personal
  or confidential documents in CI or publicly available demo deployments.
