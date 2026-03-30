"""Database connection URL helpers."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from shared.config import load_database_settings as load_runtime_database_settings


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str
    schema: str = "raw"

    @property
    def sqlalchemy_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        return f"postgresql+psycopg://{user}:{password}@{self.host}:{self.port}/{self.database}"

    @property
    def atlas_url(self) -> str:
        user = quote_plus(self.user)
        password = quote_plus(self.password)
        return (
            f"postgres://{user}:{password}@{self.host}:{self.port}/{self.database}"
            f"?search_path={quote_plus(self.schema)}&sslmode=disable"
        )


def load_database_settings() -> DatabaseSettings:
    settings = load_runtime_database_settings()
    return DatabaseSettings(**settings.__dict__)


DATABASE_SCHEMA = load_runtime_database_settings().schema
