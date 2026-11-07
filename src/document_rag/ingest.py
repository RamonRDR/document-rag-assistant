"""Bounded PDF inspection: no OCR, JavaScript execution, or subprocesses."""

import hashlib
from dataclasses import dataclass

import pymupdf

from document_rag.chunking import PageText
from document_rag.config import Settings


class InvalidDocument(ValueError):
    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class ExtractedPDF:
    sha256: str
    pages: list[PageText]
    page_count: int
    byte_size: int


def extract_pdf(
    data: bytes, filename: str, content_type: str | None, settings: Settings
) -> ExtractedPDF:
    if not filename.lower().endswith(".pdf"):
        raise InvalidDocument("Only .pdf documents are supported")
    if content_type not in ("application/pdf", "application/octet-stream", None):
        raise InvalidDocument("Invalid upload content type")
    if len(data) > settings.max_upload_bytes:
        raise InvalidDocument("PDF exceeds size limit", 413)
    if not data.startswith(b"%PDF-"):
        raise InvalidDocument("Invalid PDF header")
    try:
        with pymupdf.open(stream=data, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise InvalidDocument("Password-protected PDFs are not supported")
            if len(pdf) == 0:
                raise InvalidDocument("PDF has no pages")
            if len(pdf) > settings.max_pages:
                raise InvalidDocument("PDF exceeds page limit", 413)
            count = len(pdf)
            total = 0
            pages = []
            for index, page in enumerate(pdf):
                content = page.get_text("text", sort=True)
                total += len(content)
                if total > settings.max_document_chars:
                    raise InvalidDocument("PDF text exceeds processing limit", 413)
                if content.strip():
                    pages.append(PageText(number=index + 1, text=content))
    except InvalidDocument:
        raise
    except (RuntimeError, ValueError, pymupdf.FileDataError) as exc:
        raise InvalidDocument("Unreadable or corrupted PDF") from exc
    if not pages:
        raise InvalidDocument("PDF contains no extractable text; OCR is not enabled")
    return ExtractedPDF(
        sha256=hashlib.sha256(data).hexdigest(),
        pages=pages,
        page_count=count,
        byte_size=len(data),
    )
