"""Engine and session helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import create_engine as sqlalchemy_create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from shared.db.settings import load_database_settings


@lru_cache(maxsize=1)
def create_engine() -> Engine:
    return sqlalchemy_create_engine(load_database_settings().sqlalchemy_url, future=True)


@lru_cache(maxsize=1)
def create_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=create_engine(), autoflush=False, expire_on_commit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = create_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
