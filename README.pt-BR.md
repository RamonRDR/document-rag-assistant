<div align="center">

# Document RAG Assistant 📚

**Converse com seus PDFs. Confira cada fonte. Mantenha a recuperação rastreável.**

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

![pytest 33 passing](https://img.shields.io/badge/pytest-33%20passing-0A9EDC)
![Ruff lint & format](https://img.shields.io/badge/Ruff-lint%20%26%20format-8D9D1C)
![DB integration tests](https://img.shields.io/badge/PostgreSQL-integration%20tested-4A8D6A)
![RAG evaluation 25](https://img.shields.io/badge/RAG%20eval-25%20fictitious%20questions-795F8B)
![Docker build CI](https://img.shields.io/badge/Docker%20build-CI%20verified-276A9D)
![OpenAPI](https://img.shields.io/badge/OpenAPI-Swagger%20UI-6BA539)

</div>

> **Status do projeto:** Implementado na [PR #1](https://github.com/RamonRDR/document-rag-assistant/pull/1), **sem merge** na `main`. O apontamento de concorrência do Codex foi corrigido; o problema de pós-filtragem HNSW foi tratado com busca exata restrita e varredura iterativa geral. O GitHub Actions valida a implementação e 33 testes automatizados. Uma nova revisão do Codex pode ser necessária; sem deploy.

## Visão geral

API e demonstração local para perguntas sobre PDFs, com fontes rastreáveis, desenvolvida para um portfólio internacional de Python/backend e engenharia de IA aplicada. O destaque está no **pipeline de recuperação**, não em uma interface de chat: extração de PDFs, referência às páginas originais, fragmentação (chunking), vetores indexados, busca textual, fusão de rankings, proveniência e avaliação determinística.

**Público-alvo:** recrutadores internacionais e profissionais que avaliam Python, APIs, persistência de dados e implementação de RAG. O `README.md` em inglês é a versão principal; as versões em português e espanhol apresentam as mesmas funcionalidades, instruções e limitações.

## Funcionalidades implementadas

- Upload de PDFs com verificação de extensão, MIME/cabeçalho, limites de bytes, páginas e caracteres; erros explícitos para PDFs corrompidos, protegidos por senha ou sem texto extraível.
- Deduplicação SHA-256 de **bytes de PDFs idênticos**, identificadores únicos, listagem e consulta de metadados e exclusão. PDFs gerados novamente a partir do mesmo texto podem ter hashes diferentes.
- Normalização e chunking por página, tamanho e sobreposição configuráveis, páginas de origem e identificadores de modelos, vetores de 1536 dimensões.
- Recuperação cosseno pgvector: varredura iterativa HNSW para consultas gerais e classificação exata após filtragem por documento/modelo nas consultas restritas; full-text search em inglês e combinação híbrida por **Reciprocal Rank Fusion (RRF)**, sem duplicatas e com filtragem conservadora de evidência.
- Endpoint `POST /search` independente, com pontuação específica por estratégia, e `POST /ask`, que devolve resposta fundamentada nas fontes recuperadas ou informa ausência de evidência.
- Baseline lexical determinístico local e prévia de resposta extrativa; **integração opcional e não validada com OpenAI** por adaptadores intercambiáveis.
- Reindexação transacional a partir do texto persistido, bloqueio de linha PostgreSQL por documento para serializar requisições concorrentes, exclusão em cascata dos chunks e embeddings e chave de API nas operações sobre documentos e consultas.
- Interface web local, OpenAPI/Swagger UI, Docker Compose e testes nos runners do GitHub, **sem chamadas pagas** no CI.

## Stack tecnológica

| Camada | Tecnologia e versão/capacidade verificada |
| --- | --- |
| Linguagem e execução | Python **3.14** no Docker e CI; requisito do projeto Python `>=3.14` |
| API e validação | FastAPI `>=0.115,<1`; Pydantic **v2**, Pydantic Settings, Uvicorn ASGI, python-multipart |
| Banco de dados | PostgreSQL **17** pela imagem `pgvector/pgvector:pg17`; SQLAlchemy **2.x**, psycopg **3**, pgvector, Alembic |
| PDF | PyMuPDF (mínimo declarado `1.26.6`) |
| RAG | Baseline local de hashing lexical em 1536d, busca cosseno pgvector, FTS PostgreSQL em inglês, RRF e citações estruturadas |
| Provedor opcional | SDK Python OpenAI e adaptadores (declarados, **sem testes com provedor externo no CI**) |
| Testes e build | pytest, FastAPI TestClient baseado em httpx, Ruff, empacotamento Hatchling, Docker e Docker Compose |
| Automação | Runners hospedados do GitHub Actions; migrações, testes unitários/API/banco, avaliação fictícia da recuperação e build Docker |

Valores com `>=` representam **versões mínimas declaradas**, não a versão exata do pacote resolvido. `pytest-cov` está nas dependências de desenvolvimento, mas o workflow **não mede cobertura**. Não há **verificação mypy** no CI.

## Arquitetura

```text
Upload PDF → PyMuPDF → páginas extraídas → chunks por página
                                              ↓
                                      adaptador embedding
                                              ↓
                                     PostgreSQL + pgvector
                                              ↓
Pergunta → busca vetorial / FTS inglês → RRF + filtro de evidências
                                              ↓
                                    contexto limitado às fontes
                                              ↓
                             resposta extrativa ou LLM opcional
                                              ↓
                              resposta + documento/página citados
```

Três tabelas armazenam documentos, páginas extraídas e chunks com metadados de origem. Os bytes originais do PDF são **descartados** depois da extração; texto e embeddings permanecem até a exclusão. A reindexação usa os textos salvos e faz commit de forma atômica, com bloqueio da linha do documento para serializar requisições concorrentes. O conteúdo recuperado é dado não confiável, nunca comando executável.

Detalhes adicionais em [arquitetura](docs/architecture.md) e [segurança](docs/security.md).

## Pré-requisitos

- Recomendado: Docker Engine com Docker Compose, portas **8000** e **5432** disponíveis no localhost.
- Alternativa: Python **3.14**, PostgreSQL **17** com extensão `vector` e ambiente virtual Python.
- Uma chave nova em `RAG_API_KEY` com pelo menos **24 caracteres**. O modo local padrão **não exige chave OpenAI**.

## Instalação e execução com Docker Compose

```bash
cp .env.example .env
# Substitua RAG_API_KEY no .env por um segredo aleatório com 24+ caracteres.
docker compose up --build
```

No Windows PowerShell, utilize `Copy-Item .env.example .env` no lugar de `cp`, se necessário. O Compose aguarda a verificação de saúde do banco, executa `alembic upgrade head` e inicia o Uvicorn.

- Demonstração: http://localhost:8000/
- Documentação interativa: http://localhost:8000/docs
- Especificação OpenAPI: http://localhost:8000/openapi.json
- Verificação de vida: http://localhost:8000/health

O Compose publica API e banco somente em `127.0.0.1`. A senha `local-only-password` é um exemplo **apenas para desenvolvimento local**. Não exponha essa configuração à internet.

## Configuração

O arquivo [.env.example](.env.example) apresenta as principais variáveis. Todas as opções da aplicação utilizam o prefixo `RAG_`.

| Variável | Padrão/objetivo |
| --- | --- |
| `RAG_API_KEY` | **Obrigatória**, segredo privado de pelo menos 24 caracteres |
| `RAG_DATABASE_URL` | String de conexão PostgreSQL; Compose substitui o host por `db` |
| `RAG_EMBEDDING_PROVIDER` | `local` ou `openai`; padrão `local` |
| `RAG_LLM_PROVIDER` | `extractive` ou `openai`; padrão `extractive` |
| `RAG_OPENAI_API_KEY` | Obrigatória **somente se um provedor OpenAI for selecionado** |
| `RAG_OPENAI_EMBEDDING_MODEL` | Padrão `text-embedding-3-small`, esperando 1536 dimensões |
| `RAG_OPENAI_CHAT_MODEL` | Padrão `gpt-4o-mini` |
| `RAG_MAX_UPLOAD_BYTES` / `RAG_MAX_PAGES` | Padrão **5.000.000 bytes / 60 páginas** |
| `RAG_CHUNK_SIZE` / `RAG_CHUNK_OVERLAP` | Padrão **900 / 150** caracteres |
| `RAG_MAX_TOP_K` / `RAG_MAX_CONTEXT_CHARS` | Padrão **10 / 8000** |
| `RAG_MIN_VECTOR_SCORE` | Padrão **0.10**; não é probabilidade calibrada |

Não faça commit de `.env`, chaves ou PDFs confidenciais.

## Instalação local com Python

Inicie o PostgreSQL com pgvector, configure `RAG_DATABASE_URL` e `RAG_API_KEY`, e execute:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
alembic upgrade head
uvicorn document_rag.api:app --reload
```

No PowerShell, ative o ambiente com `.venv\Scripts\Activate.ps1`. Use um banco de testes descartável para experimentos.

## Uso da interface e da API

Na demonstração local, informe `RAG_API_KEY`, selecione um PDF, carregue-o e faça perguntas. É possível inspecionar os chunks separadamente, mudar a estratégia de busca e consultar arquivo, página e trechos de origem. A interface mantém a chave apenas na memória da aba e **não foi preparada para hospedagem pública**.

**Upload (201):**

```bash
curl -X POST http://localhost:8000/documents -H "X-API-Key: YOUR_KEY" -F "file=@sample.pdf"
```

**Consultar trechos recuperados:**

```bash
curl -X POST http://localhost:8000/search -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What does the document say about the policy?","mode":"hybrid","top_k":5}'
```

**Responder com fontes:**

```bash
curl -X POST http://localhost:8000/ask -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"question":"What does the document say about the policy?","mode":"hybrid","top_k":5}'
```

Os comandos exemplificam solicitações e **não comprovam precisão das respostas do modelo**. Os retornos incluem IDs de chunk/documento, arquivo, página original, trechos, tempos e, se disponível, quantidade de tokens do provedor.

## Referência da API REST

Todos os endpoints abaixo, exceto interface, vida e OpenAPI/Swagger, exigem `X-API-Key`.

| Método | Caminho | Finalidade |
| --- | --- | --- |
| GET | `/health` | Vida do serviço, **não** prontidão do banco |
| GET | `/` | Interface HTML local |
| POST | `/documents` | Upload e indexação síncrona de PDF |
| GET | `/documents` | Listar até 200 metadados de documentos |
| GET | `/documents/{document_id}` | Consultar metadados |
| DELETE | `/documents/{document_id}` | Excluir documento, páginas e vetores |
| POST | `/documents/{document_id}/reindex` | Reconstruir embeddings transacionalmente |
| POST | `/search` | Resultados e pontuações de busca textual, vetorial ou híbrida |
| POST | `/ask` | Resposta, citações ou ausência explícita de evidência |
| GET | `/docs` / `/openapi.json` | Swagger UI / especificação OpenAPI |

`mode` aceita `text`, `vector` ou `hybrid`, e `document_ids` restringe a consulta opcionalmente. Distância cosseno, `ts_rank` e RRF têm **escalas de pontuação diferentes**.

## Provedores e avaliação de qualidade

O embedding padrão `local` utiliza hashing normalizado de tokens, **não um modelo semântico**. O modo `extractive` devolve uma prévia do trecho, **não uma resposta gerada por LLM**. Os adaptadores OpenAI foram implementados, mas chamadas pagas reais, fidelidade das respostas e latência do provedor **não foram validadas**.

A avaliação utiliza **25 perguntas fictícias (20 com resposta, 5 sem resposta)** e compara duas configurações de chunk/overlap e três estratégias de recuperação numa transação PostgreSQL revertida ao final. As métricas são Recall@K, Precision@K, MRR@K, tempo de busca e taxa de ausência de resultado para perguntas não respondíveis. No [CI #6](https://github.com/RamonRDR/document-rag-assistant/actions/runs/42419199438), o Recall@1 do baseline lexical foi **95% na busca vetorial, 100% na textual e 100% na híbrida**, com as cinco perguntas sem evidência não retornando resultados nesse pequeno conjunto sintético. Isso **não comprova** precisão semântica geral, fidelidade de geração ou resistência a injeção de prompt.

## Testes automatizados, CI e manutenção dos badges

```bash
ruff check .
ruff format --check .
alembic upgrade head
pytest -q
python -m document_rag.evaluation --output eval-report.json
docker build -t document-rag-assistant:local .
```

O [workflow de CI](.github/workflows/ci.yml) roda em PRs para `main` e por execução manual. Usa Python 3.14 e um PostgreSQL 17/pgvector temporário, com dados fictícios; verifica Ruff, migrações, testes unitários/integração, avaliação determinística e build Docker. **Não faz merge, deploy, chamadas a LLM pago ou uso de runner pessoal**.

**Origem dos indicadores:** `pytest | 33 passing` é uma contagem estática conferida com o relatório JUnit real pelo CI da PR, **não uma contagem atualizada automaticamente pelo badge**. Uma checagem leve no CI confronta os três READMEs com o relatório JUnit real do pytest. Se a suíte mudar, atualize as três contagens na mesma PR. O badge de CI é dinâmico e acompanha as execuções de pull request deste repositório (a branch ainda não foi integrada à main). Não mostramos cobertura ou tipagem aprovadas porque essas verificações não são executadas.

## Segurança e privacidade

As rotas de documentos e consultas usam segredo de API com comprimento mínimo e comparação em tempo constante. Os limites de upload rejeitam arquivos malformados, grandes, protegidos e PDFs sem texto; a interface exibe conteúdo não confiável como texto, não HTML executável. O serviço não executa scripts ou comandos contidos em PDFs. O adaptador OpenAI pode transmitir perguntas e contexto documental a terceiros **somente quando configurado explicitamente**, com possíveis custos e questões de privacidade.

É uma **demonstração local de operador único**, não um SaaS público ou multi-tenant endurecido. Faltam autorização individual por documento, rate limiting, controle de requisição no proxy de entrada, sandbox do parser, antivírus, auditoria e tratamento de segredos em produção. A exclusão remove registros ativos do banco, não necessariamente backups externos. Veja [segurança](docs/security.md).

## Limitações conhecidas

- Sem OCR, fila de ingestão, painel de progresso ou streaming de tokens; documentos grandes são intencionalmente limitados.
- Sem autenticação de produção, isolamento entre tenants, TLS ou configuração de deploy.
- Parsing PDF ainda pode ter vulnerabilidades nativas; prompts não garantem defesa completa contra prompt injection.
- As fontes são recuperadas de chunks persistidos, mas não provam que toda afirmação gerada esteja correta.
- Integração OpenAI é opcional e **não verificada no CI**. Não há benchmarks reais de qualidade ou custo por token.
- Projeto permanece em PR, aguardando revisão final autorizada do Codex antes de eventual merge.

## Estrutura do repositório

| Caminho | Responsabilidade |
| --- | --- |
| `src/document_rag/api.py` | Rotas FastAPI, chave e OpenAPI |
| `src/document_rag/ingest.py` | Validação e extração PyMuPDF |
| `src/document_rag/chunking.py` | Criação de chunks por página |
| `src/document_rag/indexing.py` | Ingestão e reindexação transacionais |
| `src/document_rag/retrieval.py` | pgvector, FTS inglês e RRF |
| `src/document_rag/providers.py` | Adaptadores local/OpenAI |
| `src/document_rag/service.py` | Contexto limitado e respostas com fontes |
| `src/document_rag/models.py` / `db.py` | Esquema e sessões SQLAlchemy |
| `src/document_rag/evaluation.py` / `evaluation/` | Avaliação fictícia da recuperação |
| `src/document_rag/ui.py` | Interface local HTML |
| `migrations/` | Migração Alembic |
| `tests/` | Testes unitários e integração PostgreSQL |
| `.github/workflows/ci.yml` | Etapas de qualidade hospedadas |
| `scripts/` | Conferência da quantidade de testes nos badges |
| `docs/` | Decisões de arquitetura e segurança |

## Evoluções possíveis

Com escopo separado e validação específica: OCR, indexação assíncrona, autorização por documento, demo público seguro, streaming, benchmark de modelos semânticos e avaliação de fidelidade das respostas. Nenhuma dessas melhorias é anunciada como concluída.

## Contribuições e revisão

Proponha mudanças pontuais com testes e documentação em branch própria. Utilize dados fictícios e mantenha provedores pagos externos desativados no CI obrigatório. Esta PR exige revisão Codex autorizada e aprovação explícita do proprietário antes do merge.

## Licença

[Licença MIT](LICENSE), copyright © 2026 Ramon Rodriguez.
