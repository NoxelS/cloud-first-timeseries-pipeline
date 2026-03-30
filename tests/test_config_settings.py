from __future__ import annotations

import pytest

from shared.config.settings import heartbeat_cron, load_database_settings, load_heartbeat_settings, load_kafka_settings


def test_database_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_HOST", "localhost")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("DATABASE_NAME", "app")
    monkeypatch.setenv("DATABASE_USER", "user")
    monkeypatch.setenv("DATABASE_PASSWORD", "pass")
    monkeypatch.setenv("DATABASE_SCHEMA", "raw")
    load_database_settings.cache_clear()

    settings = load_database_settings()

    assert settings.host == "localhost"
    assert settings.database == "app"
    assert settings.schema == "raw"


def test_kafka_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    monkeypatch.setenv("KAFKA_DEFAULT_PARTITIONS", "5")
    monkeypatch.setenv("KAFKA_DEFAULT_REPLICATION", "1")
    load_kafka_settings.cache_clear()

    settings = load_kafka_settings()

    assert settings.bootstrap_servers == "localhost:9092"
    assert settings.default_partitions == 5


def test_heartbeat_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEARTBEAT_INTERVAL_MINUTES", "10")
    monkeypatch.setenv("HEARTBEAT_INCLUDE_INTERNAL_TOPICS", "true")
    load_heartbeat_settings.cache_clear()

    settings = load_heartbeat_settings()

    assert settings.interval_minutes == 10
    assert settings.include_internal_topics is True


def test_heartbeat_cron_defaults_to_15_minutes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEARTBEAT_INTERVAL_MINUTES", raising=False)
    load_heartbeat_settings.cache_clear()

    assert heartbeat_cron() == "*/15 * * * *"
