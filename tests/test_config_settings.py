from __future__ import annotations

import pytest

from shared.config.settings import load_database_settings, load_energy_charts_settings, load_kafka_settings


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


def test_energy_charts_settings_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENERGY_CHARTS_REGION", "CH-Zurich")
    monkeypatch.setenv("ENERGY_CHARTS_OVERLAP_SECONDS", "120")
    monkeypatch.setenv("ENERGY_CHARTS_SAFETY_LAG_SECONDS", "15")
    monkeypatch.setenv("ENERGY_CHARTS_INITIAL_LOOKBACK_HOURS", "12")
    monkeypatch.setenv("BACKFILL_MIN_COMPLETE_DAY_ROWS", "100")
    monkeypatch.setenv("BACKFILL_CHUNK_DAYS", "2")
    load_energy_charts_settings.cache_clear()

    settings = load_energy_charts_settings()

    assert settings.region == "CH-Zurich"
    assert settings.overlap_seconds == 120
    assert settings.backfill_chunk_days == 2
