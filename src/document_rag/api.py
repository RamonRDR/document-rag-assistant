"""FastAPI endpoints. Every document operation requires a user-configured API key."""
import hmac
from pathlib import PurePosixPath
from typing import Annotated

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from document_rag.config import get_settings
from document_rag.db import get_db
from document_rag.indexing import persist_pdf, reindex
from document_rag.ingest import InvalidDocument, extract_pdf
from document_rag.models import Document
from document_rag.providers import ProviderError
from document_rag.retrieval import search
from document_rag.schemas import AskResponse, DocumentOut, SearchRequest, SearchResponse
from document_rag.service import answer_question

app = FastAPI(title="Document RAG Assistant", version="0.1.0")
Db = Annotated[Session, Depends(get_db)]


def require_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    expected = get_settings().api_key.get_secret_value()
    if x_api_key is None or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")


Auth = Annotated[None, Depends(require_key)]


@app.middleware("http")
async def secure_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def demo():
    from document_rag.ui import HTML

    return HTML


@app.post("/documents", response_model=DocumentOut, status_code=201)
def upload_document(
    file: Annotated[UploadFile, File()], session: Db, _auth: Auth
):
    settings = get_settings()
    filename = PurePosixPath((file.filename or "").replace("\\", "/")).name
    if not filename or len(filename) > 255:
        raise HTTPException(status_code=422, detail="Invalid filename")
    data = file.file.read(settings.max_upload_bytes + 1)
    try:
        extracted = extract_pdf(data, filename, file.content_type, settings)
    except InvalidDocument as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    if session.scalar(select(Document.id).where(Document.sha256 == extracted.sha256)):
        raise HTTPException(status_code=409, detail="Document already indexed")
    try:
        document = persist_pdf(session, extracted, filename, settings)
        session.commit()
        session.refresh(document)
        return document
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Document already indexed") from exc
    except ProviderError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        session.rollback()
        raise


@app.get("/documents", response_model=list[DocumentOut])
def list_documents(session: Db, _auth: Auth):
    return session.scalars(select(Document).order_by(Document.created_at.desc()).limit(200)).all()


@app.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, session: Db, _auth: Auth):
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, session: Db, _auth: Auth):
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    session.delete(document)
    session.commit()


@app.post("/documents/{document_id}/reindex")
def reindex_document(document_id: str, session: Db, _auth: Auth):
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        count = reindex(session, document, get_settings())
        session.commit()
        return {"document_id": document.id, "chunks": count, "status": "ready"}
    except ProviderError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        session.rollback()
        raise


@app.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest, session: Db, _auth: Auth):
    try:
        return search(session, request, get_settings())
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/ask", response_model=AskResponse)
def ask_documents(request: SearchRequest, session: Db, _auth: Auth):
    try:
        return answer_question(session, request, get_settings())
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
