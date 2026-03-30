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


def _env_bool(name: str, default: bool) -> bool:
    value = _env(name, str(default))
    return value.strip().lower() in {"1", "true", "yes", "on"}


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
class HeartbeatSettings:
    interval_minutes: int
    include_internal_topics: bool
    lag_group_id: str


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
def load_heartbeat_settings() -> HeartbeatSettings:
    return HeartbeatSettings(
        interval_minutes=_env_int("HEARTBEAT_INTERVAL_MINUTES", 15),
        include_internal_topics=_env_bool("HEARTBEAT_INCLUDE_INTERNAL_TOPICS", False),
        lag_group_id=_env("HEARTBEAT_LAG_GROUP_ID", "heartbeat-consumer-group"),
    )


def heartbeat_cron() -> str:
    interval = load_heartbeat_settings().interval_minutes
    if interval < 1:
        raise ValueError("HEARTBEAT_INTERVAL_MINUTES must be >= 1")  # noqa: TRY003
    if interval == 1:
        return "* * * * *"
    return f"*/{interval} * * * *"
