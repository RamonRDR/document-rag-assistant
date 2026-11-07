"""SQLAlchemy session and engine. Schema creation belongs to Alembic."""
from functools import lru_cache
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from document_rag.config import get_settings


@lru_cache
def session_factory() -> sessionmaker[Session]:
    engine = create_engine(get_settings().database_url, pool_pre_ping=True, pool_size=5)
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with session_factory()() as session:
        yield session
