from __future__ import annotations

import datetime
from collections.abc import Iterator

import psycopg
import pytest
from sqlalchemy import delete, inspect
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from shared.db.models import EnergyChartsFrequency, EnergyChartsIngestionState
from shared.db.repositories import day_row_count, get_ingestion_state, upsert_frequency_events, upsert_ingestion_state
from shared.db.session import create_engine, create_session_factory
from shared.energy_charts.events import FrequencyRecord


@pytest.fixture()
def integration_session(monkeypatch: pytest.MonkeyPatch) -> Iterator[Session]:
    monkeypatch.setenv("DATABASE_HOST", "localhost")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("DATABASE_NAME", "airflow")
    monkeypatch.setenv("DATABASE_USER", "airflow")
    monkeypatch.setenv("DATABASE_PASSWORD", "airflow")
    monkeypatch.setenv("DATABASE_SCHEMA", "raw")

    create_engine.cache_clear()
    create_session_factory.cache_clear()

    try:
        engine = create_engine()
        with engine.connect():
            pass
    except (OperationalError, psycopg.OperationalError) as exc:
        pytest.skip(f"Postgres integration database is not available: {exc}")

    session = create_session_factory()()
    try:
        yield session
    finally:
        session.rollback()
        session.execute(
            delete(EnergyChartsFrequency).where(EnergyChartsFrequency.series_id == "integration::grid_frequency")
        )
        session.execute(
            delete(EnergyChartsIngestionState).where(
                EnergyChartsIngestionState.series_id == "integration::grid_frequency"
            )
        )
        session.commit()
        session.close()
        engine.dispose()


@pytest.mark.integration
def test_raw_tables_exist(integration_session: Session) -> None:
    assert integration_session.bind is not None
    inspector = inspect(integration_session.bind)
    tables = set(inspector.get_table_names(schema="raw"))
    assert "energy_charts_frequency" in tables
    assert "energy_charts_ingestion_state" in tables


@pytest.mark.integration
def test_frequency_and_state_repositories(integration_session: Session) -> None:
    event_timestamp = datetime.datetime(2026, 3, 14, 12, 0, tzinfo=datetime.timezone.utc)
    collected_at = event_timestamp + datetime.timedelta(seconds=1)

    result = upsert_frequency_events(
        integration_session,
        [
            FrequencyRecord(
                event_id="event-1",
                series_id="integration::grid_frequency",
                event_timestamp=event_timestamp,
                frequency_hz=49.98,
                source_region="DE-Freiburg",
                request_id="request-1",
                collected_at=collected_at,
            )
        ],
    )
    upsert_ingestion_state(
        integration_session,
        series_id="integration::grid_frequency",
        pipeline_name="integration-test",
        last_ingested_ts=event_timestamp,
        backfill_cursor_date=datetime.date(2026, 3, 13),
        status="live",
    )
    integration_session.commit()

    assert result.rows_written == 1
    assert result.max_event_timestamp == event_timestamp
    assert day_row_count(integration_session, series_id="integration::grid_frequency", day=event_timestamp.date()) == 1

    state = get_ingestion_state(
        integration_session,
        series_id="integration::grid_frequency",
        pipeline_name="integration-test",
    )
    assert state is not None
    assert state.status == "live"
    assert state.last_ingested_ts == event_timestamp
