FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system rag && adduser --system --ingroup rag rag
COPY pyproject.toml README.md ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
RUN pip install --no-cache-dir .
USER rag
EXPOSE 8000
CMD ["uvicorn", "document_rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
