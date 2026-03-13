"""Incrementally ingest second-level Energy Charts frequency data into the raw store."""

# ruff: noqa: S608

from __future__ import annotations

import datetime
import logging
import os
import uuid
from typing import Any

import psycopg
from airflow.decorators import dag, task

from shared.adapters.energy_charts.collector import collect_frequency_events_for_range
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics

logger = logging.getLogger(__name__)

_RAW_SCHEMA = os.environ.get("RAW_SCHEMA", "raw")
_PIPELINE_NAME = "energy-charts-feature-pipeline"
_OVERLAP_SECONDS = int(os.environ.get("ENERGY_CHARTS_OVERLAP_SECONDS", "60"))
_SAFETY_LAG_SECONDS = int(os.environ.get("ENERGY_CHARTS_SAFETY_LAG_SECONDS", "30"))
_INITIAL_LOOKBACK_HOURS = int(os.environ.get("ENERGY_CHARTS_INITIAL_LOOKBACK_HOURS", "24"))


def _db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["FEAST_OFFLINE_STORE_HOST"],
        port=int(os.environ.get("FEAST_OFFLINE_STORE_PORT", "5432")),
        dbname=os.environ["FEAST_OFFLINE_STORE_DATABASE"],
        user=os.environ["FEAST_OFFLINE_STORE_USER"],
        password=os.environ["FEAST_OFFLINE_STORE_PASSWORD"],
    )


def _parse_iso_ts(value: str) -> datetime.datetime:
    parsed = value.replace("Z", "+00:00") if value.endswith("Z") else value
    dt = datetime.datetime.fromisoformat(parsed)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _ensure_tables(conn: psycopg.Connection) -> None:
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_RAW_SCHEMA}")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_RAW_SCHEMA}.energy_charts_frequency (
                event_id TEXT NOT NULL,
                series_id TEXT NOT NULL,
                event_timestamp TIMESTAMPTZ NOT NULL,
                frequency_hz DOUBLE PRECISION NULL,
                source_region TEXT NOT NULL,
                request_id TEXT NOT NULL,
                collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_energy_charts_frequency_series_ts UNIQUE (series_id, event_timestamp)
            )
            """
        )
        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_raw_energy_charts_frequency_event_ts
            ON {_RAW_SCHEMA}.energy_charts_frequency (event_timestamp)
            """
        )
        cursor.execute(
            """
            SELECT 1
            FROM pg_indexes
            WHERE schemaname = %s
              AND tablename = 'energy_charts_frequency'
              AND indexname = 'ux_raw_energy_charts_frequency_series_ts'
            """,
            (_RAW_SCHEMA,),
        )
        has_unique_index = cursor.fetchone() is not None
        if not has_unique_index:
            cursor.execute("SELECT pg_advisory_lock(hashtext(%s))", (f"{_RAW_SCHEMA}.energy_charts_frequency.unique",))
            try:
                cursor.execute(
                    """
                    SELECT 1
                    FROM pg_indexes
                    WHERE schemaname = %s
                      AND tablename = 'energy_charts_frequency'
                      AND indexname = 'ux_raw_energy_charts_frequency_series_ts'
                    """,
                    (_RAW_SCHEMA,),
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        f"""
                        DELETE FROM {_RAW_SCHEMA}.energy_charts_frequency target
                        USING (
                            SELECT ctid
                            FROM (
                                SELECT
                                    ctid,
                                    ROW_NUMBER() OVER (
                                        PARTITION BY series_id, event_timestamp
                                        ORDER BY collected_at DESC, ctid DESC
                                    ) AS row_num
                                FROM {_RAW_SCHEMA}.energy_charts_frequency
                            ) ranked
                            WHERE ranked.row_num > 1
                        ) duplicates
                        WHERE target.ctid = duplicates.ctid
                        """
                    )
                    cursor.execute(
                        f"""
                        CREATE UNIQUE INDEX IF NOT EXISTS ux_raw_energy_charts_frequency_series_ts
                        ON {_RAW_SCHEMA}.energy_charts_frequency (series_id, event_timestamp)
                        """
                    )
            finally:
                cursor.execute("SELECT pg_advisory_unlock(hashtext(%s))", (f"{_RAW_SCHEMA}.energy_charts_frequency.unique",))
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_RAW_SCHEMA}.energy_charts_ingestion_state (
                series_id TEXT NOT NULL,
                pipeline_name TEXT NOT NULL,
                last_ingested_ts TIMESTAMPTZ NULL,
                backfill_cursor_date DATE NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                status TEXT NOT NULL DEFAULT 'idle',
                PRIMARY KEY (series_id, pipeline_name)
            )
            """
        )


def _series_id_for_region(region: str) -> str:
    return f"{region.lower()}::grid_frequency"


@dag(
    dag_id="energy-charts-feature-pipeline",
    description="Incremental raw frequency ingestion with cursor-based windows.",
    schedule="*/5 * * * *",
    start_date=datetime.datetime(2026, 3, 13),
    catchup=False,
    tags=["energy-charts", "raw"],
)
def energy_charts_feature_pipeline() -> None:  # noqa: C901
    @task()
    def prepare_window() -> dict[str, Any]:
        region = os.environ.get("ENERGY_CHARTS_REGION", "DE-Freiburg")
        series_id = _series_id_for_region(region)
        window_end = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(seconds=_SAFETY_LAG_SECONDS)

        with _db_connection() as conn:
            _ensure_tables(conn)
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT last_ingested_ts
                    FROM {_RAW_SCHEMA}.energy_charts_ingestion_state
                    WHERE series_id = %s AND pipeline_name = %s
                    """,
                    (series_id, _PIPELINE_NAME),
                )
                row = cursor.fetchone()

        if row and row[0]:
            last_ingested_ts = row[0].astimezone(datetime.timezone.utc)
            window_start = last_ingested_ts - datetime.timedelta(seconds=_OVERLAP_SECONDS)
        else:
            window_start = window_end - datetime.timedelta(hours=_INITIAL_LOOKBACK_HOURS)

        if window_start >= window_end:
            window_start = window_end - datetime.timedelta(minutes=1)

        return {
            "request_id": str(uuid.uuid4()),
            "region": region,
            "series_id": series_id,
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
        }

    @task()
    def collect_raw_events(window: dict[str, Any]) -> dict[str, Any]:
        payload = collect_frequency_events_for_range(
            window_start=_parse_iso_ts(window["window_start"]),
            window_end=_parse_iso_ts(window["window_end"]),
            region=window["region"],
            request_id=window["request_id"],
        )
        payload["series_id"] = window["series_id"]
        logger.info(
            "Collected %d raw frequency events for %s -> %s",
            len(payload.get("events", [])),
            payload["window_start"],
            payload["window_end"],
        )
        return payload

    @task()
    def write_raw_table(payload: dict[str, Any]) -> dict[str, Any]:
        events = payload.get("events", [])
        if not events:
            payload["rows_written"] = 0
            return payload

        max_event_ts: datetime.datetime | None = None
        with _db_connection() as conn:
            _ensure_tables(conn)
            with conn.cursor() as cursor:
                rows = []
                for event in events:
                    event_ts = _parse_iso_ts(event["event_timestamp"])
                    if max_event_ts is None or event_ts > max_event_ts:
                        max_event_ts = event_ts
                    rows.append((
                        event["event_id"],
                        event["series_id"],
                        event_ts,
                        event.get("frequency_hz"),
                        event["source_region"],
                        event["request_id"],
                        _parse_iso_ts(event["collected_at"]),
                    ))
                cursor.executemany(
                    f"""
                    INSERT INTO {_RAW_SCHEMA}.energy_charts_frequency (
                        event_id,
                        series_id,
                        event_timestamp,
                        frequency_hz,
                        source_region,
                        request_id,
                        collected_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (series_id, event_timestamp)
                    DO UPDATE SET
                        event_id = EXCLUDED.event_id,
                        frequency_hz = EXCLUDED.frequency_hz,
                        source_region = EXCLUDED.source_region,
                        request_id = EXCLUDED.request_id,
                        collected_at = EXCLUDED.collected_at
                    """,
                    rows,
                )
                payload["rows_written"] = max(cursor.rowcount, 0)
            conn.commit()

        payload["max_event_timestamp"] = max_event_ts.isoformat() if max_event_ts else None
        return payload

    @task()
    def update_ingestion_state(payload: dict[str, Any]) -> dict[str, Any]:
        max_event_ts = payload.get("max_event_timestamp")
        if not max_event_ts:
            logger.info("No max event timestamp; ingestion cursor remains unchanged.")
            return payload

        with _db_connection() as conn, conn.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {_RAW_SCHEMA}.energy_charts_ingestion_state (
                    series_id,
                    pipeline_name,
                    last_ingested_ts,
                    updated_at,
                    status
                )
                VALUES (%s, %s, %s, NOW(), %s)
                ON CONFLICT (series_id, pipeline_name)
                DO UPDATE SET
                    last_ingested_ts = GREATEST(
                        {_RAW_SCHEMA}.energy_charts_ingestion_state.last_ingested_ts,
                        EXCLUDED.last_ingested_ts
                    ),
                    updated_at = NOW(),
                    status = EXCLUDED.status
                """,
                (payload["series_id"], _PIPELINE_NAME, _parse_iso_ts(max_event_ts), "live"),
            )
            conn.commit()
        return payload

    @task()
    def publish_raw_update_trigger(payload: dict[str, Any]) -> None:
        if payload.get("rows_written", 0) <= 0:
            logger.info("Skipping raw update trigger; no rows written.")
            return

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            "source": _PIPELINE_NAME,
            "pipeline": _PIPELINE_NAME,
            "series_id": payload["series_id"],
            "window_start": payload["window_start"],
            "window_end": payload["window_end"],
            "rows_written": payload["rows_written"],
        }
        publish_event(KafkaTopics.RAW_ENERGY_CHARTS_UPDATED.value, event)

    window = prepare_window()
    payload = collect_raw_events(window)
    payload = write_raw_table(payload)
    payload = update_ingestion_state(payload)
    publish_raw_update_trigger(payload)


energy_charts_feature_pipeline()
