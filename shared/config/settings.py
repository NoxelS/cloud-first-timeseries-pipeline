"""Typed runtime configuration for local services and scripts."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None or value == "":
        raise ValueError(f"Environment variable '{name}' must be set")  # noqa: TRY003
    return value


def _env_int(name: str, default: int) -> int:
    return int(_env(name, str(default)))


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str
    schema: str


@dataclass(frozen=True)
class KafkaSettings:
    bootstrap_servers: str
    default_partitions: int
    default_replication_factor: int


@dataclass(frozen=True)
class EnergyChartsSettings:
    region: str
    overlap_seconds: int
    safety_lag_seconds: int
    initial_lookback_hours: int
    backfill_min_complete_day_rows: int
    backfill_chunk_days: int


@lru_cache(maxsize=1)
def load_database_settings() -> DatabaseSettings:
    return DatabaseSettings(
        host=_env("DATABASE_HOST", "postgres"),
        port=_env_int("DATABASE_PORT", 5432),
        database=_env("DATABASE_NAME", "airflow"),
        user=_env("DATABASE_USER", "airflow"),
        password=_env("DATABASE_PASSWORD", "airflow"),
        schema=_env("DATABASE_SCHEMA", "raw"),
    )


@lru_cache(maxsize=1)
def load_kafka_settings() -> KafkaSettings:
    return KafkaSettings(
        bootstrap_servers=_env("KAFKA_BOOTSTRAP_SERVERS"),
        default_partitions=_env_int("KAFKA_DEFAULT_PARTITIONS", 3),
        default_replication_factor=_env_int("KAFKA_DEFAULT_REPLICATION", 1),
    )


@lru_cache(maxsize=1)
def load_energy_charts_settings() -> EnergyChartsSettings:
    return EnergyChartsSettings(
        region=_env("ENERGY_CHARTS_REGION", "DE-Freiburg"),
        overlap_seconds=_env_int("ENERGY_CHARTS_OVERLAP_SECONDS", 60),
        safety_lag_seconds=_env_int("ENERGY_CHARTS_SAFETY_LAG_SECONDS", 30),
        initial_lookback_hours=_env_int("ENERGY_CHARTS_INITIAL_LOOKBACK_HOURS", 24),
        backfill_min_complete_day_rows=_env_int("BACKFILL_MIN_COMPLETE_DAY_ROWS", 86400),
        backfill_chunk_days=_env_int("BACKFILL_CHUNK_DAYS", 3),
    )
