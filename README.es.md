<div align="center">

# Document RAG Assistant 📚

**Pregunta a tus PDFs. Examina cada fuente. Mantén la recuperación verificable.**

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

![pytest 35 passing](https://img.shields.io/badge/pytest-35%20passing-0A9EDC)
![Ruff lint & format](https://img.shields.io/badge/Ruff-lint%20%26%20format-8D9D1C)
![DB integration tests](https://img.shields.io/badge/PostgreSQL-integration%20tested-4A8D6A)
![RAG evaluation 25](https://img.shields.io/badge/RAG%20eval-25%20fictitious%20questions-795F8B)
![Docker build CI](https://img.shields.io/badge/Docker%20build-CI%20verified-276A9D)
![OpenAPI](https://img.shields.io/badge/OpenAPI-Swagger%20UI-6BA539)

</div>

> **Estado del proyecto:** Implementado en la [PR #1](https://github.com/RamonRDR/document-rag-assistant/pull/1), **sin fusionar** en `main`. Se abordaron los problemas de concurrencia y posfiltrado HNSW; la expansión de candidatos evita respuestas vacías prematuras por evidencias rechazadas. CI valida la implementación y 35 pruebas automatizadas. Puede requerirse otra revisión de Codex; sin despliegue.

## Descripción general

API y demostración local para responder preguntas sobre documentos PDF con fuentes rastreables, creada para un portafolio internacional de Python/backend e ingeniería de IA aplicada. Su propósito central es demostrar el **pipeline de recuperación**, no solo una interfaz de chat: extracción de PDF, referencias a páginas originales, fragmentación (chunking), vectores indexados, búsqueda textual, fusión de clasificaciones, procedencia y evaluación determinista.

**Público objetivo:** reclutadores internacionales e ingenieros que evalúan Python, APIs, persistencia de datos e implementaciones RAG. El `README.md` en inglés es el documento principal; las versiones en portugués y español conservan las mismas funciones, instrucciones y limitaciones.

## Funciones implementadas

- Carga validada de PDF mediante extensión, MIME/cabecera y límites de bytes, páginas y caracteres; errores explícitos para archivos dañados, protegidos por contraseña o sin texto extraíble.
- Detección SHA-256 de **bytes de PDF idénticos**, identificadores únicos, consulta/listado de metadatos y eliminación. Dos PDF regenerados desde el mismo texto pueden tener hashes distintos.
- Normalización y chunking por página, longitud y solapamiento configurables, páginas originales e identificadores de modelo, vectores de 1536 dimensiones.
- Recuperación coseno pgvector: escaneo iterativo HNSW en consultas generales y clasificación exacta tras filtrar por documento/modelo en consultas restringidas; búsqueda de texto completo en inglés y fusión híbrida mediante **Reciprocal Rank Fusion (RRF)**. La búsqueda amplía gradualmente los candidatos hasta encontrar evidencias suficientes o agotar los resultados, sin detenerse después de descartar fragmentos.
- Endpoint `POST /search` independiente, con puntuaciones específicas por estrategia, y `POST /ask` para responder con fuentes recuperadas o reconocer evidencia insuficiente.
- Línea base léxica determinista local y vista previa de respuesta extractiva; **integración opcional con OpenAI sin validar** mediante adaptadores intercambiables.
- Reindexación transaccional a partir de texto guardado, bloqueo de fila PostgreSQL por documento para serializar solicitudes concurrentes, eliminación en cascada de fragmentos y embeddings, clave API requerida para documentos y consultas.
- Interfaz web local, OpenAPI/Swagger UI, Docker Compose y pruebas en runners de GitHub, **sin llamadas de pago** en CI.

## Stack tecnológico

| Capa | Tecnología y versión/capacidad verificada |
| --- | --- |
| Lenguaje/ejecución | Python **3.14** en Docker y CI; requisito del proyecto Python `>=3.14` |
| API/validación | FastAPI `>=0.115,<1`; Pydantic **v2**, Pydantic Settings, Uvicorn ASGI, python-multipart |
| Base de datos | PostgreSQL **17** con imagen `pgvector/pgvector:pg17`; SQLAlchemy **2.x**, psycopg **3**, pgvector, Alembic |
| PDF | PyMuPDF (mínimo declarado `1.26.6`) |
| RAG | Hashing léxico local de 1536d, búsqueda coseno pgvector, FTS PostgreSQL en inglés, RRF, citas estructuradas |
| Proveedor opcional | SDK Python de OpenAI y adaptadores (declarados, **sin uso del proveedor externo en CI**) |
| Pruebas/build | pytest, FastAPI TestClient basado en httpx, Ruff, empaquetado Hatchling, imagen Docker y Docker Compose |
| Automatización | GitHub Actions con runners alojados; migraciones, pruebas unitarias/API/BD, evaluación sintética y build Docker |

Las versiones con `>=` son **mínimos declarados**, no números exactos de paquetes resueltos. `pytest-cov` está instalado para desarrollo, pero el workflow **no calcula cobertura**. **mypy no se ejecuta** en CI.

## Arquitectura

```text
Carga PDF → PyMuPDF → páginas extraídas → fragmentos por página
                                             ↓
                                     adaptador de embeddings
                                             ↓
                                    PostgreSQL + pgvector
                                             ↓
Pregunta → búsqueda vectorial / FTS inglés → RRF + filtro de evidencias
                                             ↓
                                  contexto limitado a las fuentes
                                             ↓
                             respuesta extractiva o LLM opcional
                                             ↓
                               respuesta + citas de documento/página
```

Tres tablas guardan documentos, páginas extraídas y fragmentos con metadatos de procedencia. Los bytes originales del PDF se **descartan** después de la extracción; texto y embeddings se conservan hasta su eliminación. La reindexación reconstruye los vectores desde las páginas almacenadas y realiza commit atómico, con bloqueo de la fila del documento para serializar solicitudes concurrentes. Los contenidos recuperados se consideran datos no confiables, no comandos ejecutables.

Consulta [arquitectura](docs/architecture.md) y [seguridad](docs/security.md).

## Requisitos previos

- Recomendado: Docker Engine con Docker Compose y puertos **8000** y **5432** libres en localhost.
- Alternativa: Python **3.14**, PostgreSQL **17** con extensión `vector` y entorno virtual de Python.
- Clave nueva en `RAG_API_KEY` de al menos **24 caracteres**. El modo local predeterminado **no requiere clave OpenAI**.

## Instalación y ejecución con Docker Compose

```bash
cp .env.example .env
# Sustituye RAG_API_KEY en .env por un secreto aleatorio de 24+ caracteres.
docker compose up --build
```

En Windows PowerShell puedes usar `Copy-Item .env.example .env` en lugar de `cp`. Compose espera la verificación de salud de la base de datos, ejecuta `alembic upgrade head` e inicia Uvicorn.

- Demostración: http://localhost:8000/
- Documentación interactiva: http://localhost:8000/docs
- Especificación OpenAPI: http://localhost:8000/openapi.json
- Estado de vida: http://localhost:8000/health

Compose vincula API y base de datos únicamente a `127.0.0.1`. La contraseña `local-only-password` es **exclusiva del desarrollo local**. No expongas esta configuración a internet.

## Configuración

El archivo [.env.example](.env.example) contiene las variables principales. Todas las opciones de la aplicación llevan el prefijo `RAG_`.

| Variable | Valor por defecto/propósito |
| --- | --- |
| `RAG_API_KEY` | **Obligatoria**, secreto privado de al menos 24 caracteres |
| `RAG_DATABASE_URL` | Conexión PostgreSQL; Compose sustituye el host por `db` |
| `RAG_EMBEDDING_PROVIDER` | `local` u `openai`; por defecto `local` |
| `RAG_LLM_PROVIDER` | `extractive` u `openai`; por defecto `extractive` |
| `RAG_OPENAI_API_KEY` | Obligatoria **solo si se elige un proveedor OpenAI** |
| `RAG_OPENAI_EMBEDDING_MODEL` | Por defecto `text-embedding-3-small`, espera 1536 dimensiones |
| `RAG_OPENAI_CHAT_MODEL` | Por defecto `gpt-4o-mini` |
| `RAG_MAX_UPLOAD_BYTES` / `RAG_MAX_PAGES` | Por defecto **5.000.000 bytes / 60 páginas** |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | Por defecto **900 / 150** caracteres |
| `RAG_MAX_TOP_K` / `RAG_MAX_CONTEXT_CHARS` | Por defecto **10 / 8000** |
| `RAG_MIN_VECTOR_SCORE` | Por defecto **0.10**; no es probabilidad calibrada |

No agregues `.env`, claves ni PDFs confidenciales al repositorio.

## Instalación local con Python

Inicia PostgreSQL con pgvector, establece `RAG_DATABASE_URL` y `RAG_API_KEY`, y ejecuta:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
alembic upgrade head
uvicorn document_rag.api:app --reload
```

En PowerShell, activa el entorno con `.venv\Scripts\Activate.ps1`. Utiliza una base de datos de pruebas desechable para experimentos.

## Uso de la demostración y la API

En la demostración local, introduce `RAG_API_KEY`, selecciona un PDF, súbelo y formula preguntas. Puedes inspeccionar fragmentos recuperados por separado, cambiar la estrategia de búsqueda y ver nombre de archivo, página y extractos. La interfaz mantiene la clave solo en memoria de la pestaña y **no está preparada para alojamiento público**.

**Subir PDF (201):**

```bash
curl -X POST http://localhost:8000/documents -H "X-API-Key: YOUR_KEY" -F "file=@sample.pdf"
```

**Recuperar extractos:**

```bash
curl -X POST http://localhost:8000/search -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What does the document say about the policy?","mode":"hybrid","top_k":5}'
```

**Responder con citas:**

```bash
curl -X POST http://localhost:8000/ask -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What does the document say about the policy?","mode":"hybrid","top_k":5}'
```

Son ejemplos de solicitudes y **no demuestran la precisión de respuestas del modelo**. Las respuestas contienen IDs de fragmento/documento, archivo, página original, extractos, tiempos y, cuando corresponde, tokens del proveedor.

## Referencia de la API REST

Todos los endpoints siguientes requieren `X-API-Key`, excepto la interfaz, liveness y OpenAPI/Swagger.

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/health` | Comprobación de vida, **no** preparación de la base de datos |
| GET | `/` | Interfaz HTML local |
| POST | `/documents` | Subir e indexar PDF de forma síncrona |
| GET | `/documents` | Listar hasta 200 metadatos |
| GET | `/documents/{document_id}` | Consultar metadatos |
| DELETE | `/documents/{document_id}` | Eliminar documento, páginas y vectores |
| POST | `/documents/{document_id}/reindex` | Reconstrucción transaccional de embeddings |
| POST | `/search` | Resultados y puntuaciones de búsqueda textual, vectorial o híbrida |
| POST | `/ask` | Respuesta, citas o ausencia explícita de evidencia |
| GET | `/docs` / `/openapi.json` | Swagger UI / especificación OpenAPI |

`mode` admite `text`, `vector` o `hybrid`; `document_ids` permite restringir la búsqueda. La similitud coseno, `ts_rank` y RRF utilizan **escalas diferentes**.

## Modos del proveedor y evaluación de calidad

El embedder `local` usa hashing normalizado de tokens, **no un modelo semántico**. El modo `extractive` devuelve una vista previa del extracto, **no una respuesta generada por LLM**. Los adaptadores OpenAI están implementados, pero las llamadas pagadas reales, la fidelidad de las respuestas y la latencia del proveedor **no están validadas**.

El corpus incluye **25 preguntas ficticias (20 respondibles, 5 sin respuesta)** y compara dos configuraciones de chunk/overlap y tres estrategias de recuperación en una transacción PostgreSQL revertida al terminar. Las métricas son Recall@K, Precision@K, MRR@K, latencia y proporción de preguntas sin evidencia para las que no se obtuvo ningún resultado. En [CI #6](https://github.com/RamonRDR/document-rag-assistant/actions/runs/42419199438), el Recall@1 de la línea base léxica fue **95% vectorial, 100% textual y 100% híbrido**, y las cinco preguntas sin evidencia no recuperaron resultados en ese pequeño corpus sintético. Esto **no prueba** precisión semántica general, generación fundamentada ni inmunidad contra inyección de instrucciones.

## Pruebas automatizadas, CI y mantenimiento de badges

```bash
ruff check .
ruff format --check .
alembic upgrade head
pytest -q
python -m document_rag.evaluation --output eval-report.json
docker build -t document-rag-assistant:local .
```

El [workflow CI](.github/workflows/ci.yml) se ejecuta en PRs hacia `main` y manualmente. Usa Python 3.14 y un PostgreSQL 17/pgvector temporal, con datos ficticios, y verifica Ruff, migraciones, pruebas unitarias e integración, evaluación determinista y build Docker. **No fusiona ramas, no despliega, no llama a LLM de pago ni utiliza un runner personal**.

**Origen de los indicadores:** `pytest | 35 passing` es una captura estática comprobada mediante el informe JUnit real en el CI de la PR, **no una cifra actualizada automáticamente por el badge**. Una comprobación ligera en CI compara los tres README con el resultado real de pytest en JUnit. Si cambia el conjunto de pruebas, actualiza las tres cifras en la misma PR. El badge CI es dinámico y sigue las ejecuciones de pull request de este repositorio (la rama todavía no está fusionada en main). No se muestran badges de cobertura ni de tipado aprobado porque no se ejecutan esas verificaciones.

## Seguridad y privacidad

Las operaciones de documentos y consultas requieren una clave con longitud mínima y comparación en tiempo constante. Las restricciones de carga rechazan archivos dañados, demasiado grandes, cifrados o sin texto; la interfaz presenta los contenidos como texto y no HTML ejecutable. El servidor no ejecuta scripts ni comandos de PDF. El adaptador OpenAI puede transmitir consultas y contexto documental al proveedor externo **solo si se configura explícitamente**, con posibles costes e implicaciones de privacidad.

Esta es una **demostración local para un único operador**, no un SaaS público endurecido o multiusuario. Faltan autorización individual por documento, limitación de solicitudes, control de tamaño en el proxy de entrada, sandbox de análisis PDF, antivirus, auditoría y gestión de secretos de producción. La eliminación afecta a filas activas, no necesariamente a copias externas de seguridad. Consulta [seguridad](docs/security.md).

## Limitaciones conocidas

- Sin OCR, ingestión en cola, panel de progreso ni streaming de tokens; los documentos grandes están limitados intencionalmente.
- Sin autenticación de producción, aislamiento de tenants, TLS o configuración de despliegue.
- Los analizadores PDF nativos pueden tener vulnerabilidades; los prompts no garantizan protección completa contra prompt injection.
- Las citas proceden de fragmentos recuperados, pero no garantizan que toda afirmación generada sea correcta.
- Integración OpenAI opcional y **sin validar en CI**. No hay benchmarks reales de calidad o gasto por token.
- El proyecto continúa en una PR y requiere revisión final autorizada de Codex antes de considerar una fusión.

## Estructura del repositorio

| Ruta | Responsabilidad |
| --- | --- |
| `src/document_rag/api.py` | Rutas FastAPI, clave y OpenAPI |
| `src/document_rag/ingest.py` | Validación y extracción PyMuPDF |
| `src/document_rag/chunking.py` | Fragmentación por página |
| `src/document_rag/indexing.py` | Ingestión y reindexación transaccionales |
| `src/document_rag/retrieval.py` | pgvector, FTS inglés y RRF |
| `src/document_rag/providers.py` | Adaptadores local/OpenAI |
| `src/document_rag/service.py` | Contexto limitado y respuestas citadas |
| `src/document_rag/models.py` / `db.py` | Esquema y sesiones SQLAlchemy |
| `src/document_rag/evaluation.py` / `evaluation/` | Evaluación sintética de recuperación |
| `src/document_rag/ui.py` | Interfaz HTML local |
| `migrations/` | Migraciones Alembic |
| `tests/` | Pruebas unitarias y de integración PostgreSQL |
| `.github/workflows/ci.yml` | Validaciones automatizadas |
| `scripts/` | Comprobación de recuento de pruebas en badges |
| `docs/` | Decisiones de arquitectura y seguridad |

## Posibles mejoras futuras

Con alcance y validación separados: OCR, indexación asíncrona, autorización por documento, demo público endurecido, streaming, benchmarks de modelos semánticos y evaluación de fidelidad. Ninguna se presenta como ya implementada.

## Contribuciones y revisión

Propón cambios concretos con pruebas y documentación en una rama de trabajo. Utiliza datos ficticios y mantén deshabilitados los proveedores externos de pago en CI obligatorio. Esta PR exige revisión autorizada de Codex y aprobación explícita del propietario antes de fusionarse.

## Licencia

[Licencia MIT](LICENSE), copyright © 2026 Ramon Rodriguez.
