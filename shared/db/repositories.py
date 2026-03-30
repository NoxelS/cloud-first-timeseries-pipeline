"""Small repository helpers for the raw Energy Charts tables."""

from __future__ import annotations

import datetime
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import Select, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from shared.db.models import EnergyChartsFrequency, EnergyChartsIngestionState
from shared.energy_charts.events import FrequencyRecord

_UPSERT_BATCH_SIZE = 5000


@dataclass(frozen=True)
class UpsertResult:
    rows_written: int
    max_event_timestamp: datetime.datetime | None


def upsert_frequency_events(session: Session, events: Sequence[FrequencyRecord]) -> UpsertResult:
    """Bulk upsert second-level frequency rows in safe parameter-sized batches."""
    if not events:
        return UpsertResult(rows_written=0, max_event_timestamp=None)

    rows = [
        {
            "event_id": event.event_id,
            "series_id": event.series_id,
            "event_timestamp": event.event_timestamp,
            "frequency_hz": event.frequency_hz,
            "source_region": event.source_region,
            "request_id": event.request_id,
            "collected_at": event.collected_at,
        }
        for event in events
    ]
    max_event_timestamp = max(row["event_timestamp"] for row in rows)

    for batch_start in range(0, len(rows), _UPSERT_BATCH_SIZE):
        batch = rows[batch_start : batch_start + _UPSERT_BATCH_SIZE]
        statement = insert(EnergyChartsFrequency).values(batch)
        statement = statement.on_conflict_do_update(
            index_elements=[EnergyChartsFrequency.series_id, EnergyChartsFrequency.event_timestamp],
            set_={
                "event_id": statement.excluded.event_id,
                "frequency_hz": statement.excluded.frequency_hz,
                "source_region": statement.excluded.source_region,
                "request_id": statement.excluded.request_id,
                "collected_at": statement.excluded.collected_at,
            },
        )
        session.execute(statement)

    return UpsertResult(rows_written=len(rows), max_event_timestamp=max_event_timestamp)


def day_row_count(session: Session, *, series_id: str, day: datetime.date) -> int:
    """Count stored second-level rows for a UTC day."""
    day_start = datetime.datetime.combine(day, datetime.time.min, tzinfo=datetime.timezone.utc)
    day_end = day_start + datetime.timedelta(days=1)
    statement: Select[tuple[int]] = (
        select(func.count())
        .select_from(EnergyChartsFrequency)
        .where(
            EnergyChartsFrequency.series_id == series_id,
            EnergyChartsFrequency.event_timestamp >= day_start,
            EnergyChartsFrequency.event_timestamp < day_end,
        )
    )
    return int(session.scalar(statement) or 0)


def get_ingestion_state(session: Session, *, series_id: str, pipeline_name: str) -> EnergyChartsIngestionState | None:
    return session.get(EnergyChartsIngestionState, {"series_id": series_id, "pipeline_name": pipeline_name})


def upsert_ingestion_state(
    session: Session,
    *,
    series_id: str,
    pipeline_name: str,
    last_ingested_ts: datetime.datetime | None,
    backfill_cursor_date: datetime.date | None,
    status: str,
) -> None:
    """Track the latest processed cursor for a pipeline and series."""
    statement = insert(EnergyChartsIngestionState).values(
        series_id=series_id,
        pipeline_name=pipeline_name,
        last_ingested_ts=last_ingested_ts,
        backfill_cursor_date=backfill_cursor_date,
        status=status,
    )
    statement = statement.on_conflict_do_update(
        index_elements=[EnergyChartsIngestionState.series_id, EnergyChartsIngestionState.pipeline_name],
        set_={
            "last_ingested_ts": func.coalesce(
                func.greatest(EnergyChartsIngestionState.last_ingested_ts, statement.excluded.last_ingested_ts),
                EnergyChartsIngestionState.last_ingested_ts,
                statement.excluded.last_ingested_ts,
            ),
            "backfill_cursor_date": statement.excluded.backfill_cursor_date,
            "updated_at": func.now(),
            "status": statement.excluded.status,
        },
    )
    session.execute(statement)


def set_ingestion_status(session: Session, *, series_id: str, pipeline_name: str, status: str) -> None:
    session.execute(
        update(EnergyChartsIngestionState)
        .where(
            EnergyChartsIngestionState.series_id == series_id,
            EnergyChartsIngestionState.pipeline_name == pipeline_name,
        )
        .values(status=status, updated_at=func.now())
    )
