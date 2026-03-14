from __future__ import annotations

# ruff: noqa: S608
import datetime
import json
import logging
import os
import uuid
from typing import Any

import psycopg
from kafka import KafkaConsumer

from shared.adapters.energy_charts.collector import collect_frequency_events_for_range
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics

logger = logging.getLogger(__name__)

_RAW_SCHEMA = os.environ.get("RAW_SCHEMA", "raw")
_FEAST_SCHEMA = os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")
_PIPELINE_NAME = "energy-charts-backfill-service"
_MIN_COMPLETE_DAY_ROWS = int(os.environ.get("BACKFILL_MIN_COMPLETE_DAY_ROWS", "86400"))
_BACKFILL_CHUNK_DAYS = int(os.environ.get("BACKFILL_CHUNK_DAYS", "3"))


def _db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["FEAST_OFFLINE_STORE_HOST"],
        port=int(os.environ.get("FEAST_OFFLINE_STORE_PORT", "5432")),
        dbname=os.environ["FEAST_OFFLINE_STORE_DATABASE"],
        user=os.environ["FEAST_OFFLINE_STORE_USER"],
        password=os.environ["FEAST_OFFLINE_STORE_PASSWORD"],
    )


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
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_FEAST_SCHEMA}")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_FEAST_SCHEMA}.grid_frequency_5m (
                series_id TEXT NOT NULL,
                event_timestamp TIMESTAMPTZ NOT NULL,
                source_region TEXT NULL,
                frequency_mean_hz DOUBLE PRECISION NULL,
                frequency_min_hz DOUBLE PRECISION NULL,
                frequency_max_hz DOUBLE PRECISION NULL,
                frequency_stddev_hz DOUBLE PRECISION NULL,
                sample_count BIGINT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (series_id, event_timestamp)
            )
            """
        )
        cursor.execute(
            f"ALTER TABLE {_FEAST_SCHEMA}.grid_frequency_5m ADD COLUMN IF NOT EXISTS source_region TEXT"
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_FEAST_SCHEMA}.grid_frequency_15m (
                series_id TEXT NOT NULL,
                event_timestamp TIMESTAMPTZ NOT NULL,
                source_region TEXT NULL,
                frequency_mean_hz DOUBLE PRECISION NULL,
                frequency_min_hz DOUBLE PRECISION NULL,
                frequency_max_hz DOUBLE PRECISION NULL,
                frequency_stddev_hz DOUBLE PRECISION NULL,
                sample_count BIGINT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (series_id, event_timestamp)
            )
            """
        )
        cursor.execute(
            f"ALTER TABLE {_FEAST_SCHEMA}.grid_frequency_15m ADD COLUMN IF NOT EXISTS source_region TEXT"
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_FEAST_SCHEMA}.grid_frequency_1h (
                series_id TEXT NOT NULL,
                event_timestamp TIMESTAMPTZ NOT NULL,
                source_region TEXT NULL,
                frequency_mean_hz DOUBLE PRECISION NULL,
                frequency_min_hz DOUBLE PRECISION NULL,
                frequency_max_hz DOUBLE PRECISION NULL,
                frequency_stddev_hz DOUBLE PRECISION NULL,
                sample_count BIGINT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (series_id, event_timestamp)
            )
            """
        )
        cursor.execute(
            f"ALTER TABLE {_FEAST_SCHEMA}.grid_frequency_1h ADD COLUMN IF NOT EXISTS source_region TEXT"
        )


def _parse_date(value: str) -> datetime.date:
    return datetime.date.fromisoformat(value)


def _parse_iso_ts(value: str) -> datetime.datetime:
    parsed = value.replace("Z", "+00:00") if value.endswith("Z") else value
    dt = datetime.datetime.fromisoformat(parsed)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _series_id(region: str) -> str:
    return f"{region.lower()}::grid_frequency"


def _upsert_rows(events: list[dict[str, Any]]) -> tuple[int, datetime.datetime | None]:
    if not events:
        return 0, None

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
            written = max(cursor.rowcount, 0)
        conn.commit()
    return written, max_event_ts


def _upsert_aggregates(conn: psycopg.Connection, start_ts: datetime.datetime, end_ts: datetime.datetime) -> int:
    with conn.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO {_FEAST_SCHEMA}.grid_frequency_5m (
                series_id,
                event_timestamp,
                source_region,
                frequency_mean_hz,
                frequency_min_hz,
                frequency_max_hz,
                frequency_stddev_hz,
                sample_count,
                created_at
            )
            SELECT
                series_id,
                date_bin(interval '5 minutes', event_timestamp, '1970-01-01'::timestamptz),
                MAX(source_region),
                AVG(frequency_hz),
                MIN(frequency_hz),
                MAX(frequency_hz),
                STDDEV_SAMP(frequency_hz),
                COUNT(frequency_hz),
                NOW()
            FROM {_RAW_SCHEMA}.energy_charts_frequency
            WHERE event_timestamp >= %s
              AND event_timestamp < %s
            GROUP BY series_id, date_bin(interval '5 minutes', event_timestamp, '1970-01-01'::timestamptz)
            ON CONFLICT (series_id, event_timestamp)
            DO UPDATE SET
                frequency_mean_hz = EXCLUDED.frequency_mean_hz,
                source_region = EXCLUDED.source_region,
                frequency_min_hz = EXCLUDED.frequency_min_hz,
                frequency_max_hz = EXCLUDED.frequency_max_hz,
                frequency_stddev_hz = EXCLUDED.frequency_stddev_hz,
                sample_count = EXCLUDED.sample_count,
                created_at = NOW()
            """,
            (start_ts, end_ts),
        )
        affected_5m = max(cursor.rowcount, 0)
        cursor.execute(
            f"""
            INSERT INTO {_FEAST_SCHEMA}.grid_frequency_15m (
                series_id,
                event_timestamp,
                source_region,
                frequency_mean_hz,
                frequency_min_hz,
                frequency_max_hz,
                frequency_stddev_hz,
                sample_count,
                created_at
            )
            SELECT
                series_id,
                date_bin(interval '15 minutes', event_timestamp, '1970-01-01'::timestamptz),
                MAX(source_region),
                AVG(frequency_hz),
                MIN(frequency_hz),
                MAX(frequency_hz),
                STDDEV_SAMP(frequency_hz),
                COUNT(frequency_hz),
                NOW()
            FROM {_RAW_SCHEMA}.energy_charts_frequency
            WHERE event_timestamp >= %s
              AND event_timestamp < %s
            GROUP BY series_id, date_bin(interval '15 minutes', event_timestamp, '1970-01-01'::timestamptz)
            ON CONFLICT (series_id, event_timestamp)
            DO UPDATE SET
                frequency_mean_hz = EXCLUDED.frequency_mean_hz,
                source_region = EXCLUDED.source_region,
                frequency_min_hz = EXCLUDED.frequency_min_hz,
                frequency_max_hz = EXCLUDED.frequency_max_hz,
                frequency_stddev_hz = EXCLUDED.frequency_stddev_hz,
                sample_count = EXCLUDED.sample_count,
                created_at = NOW()
            """,
            (start_ts, end_ts),
        )
        affected_15m = max(cursor.rowcount, 0)
        cursor.execute(
            f"""
            INSERT INTO {_FEAST_SCHEMA}.grid_frequency_1h (
                series_id,
                event_timestamp,
                source_region,
                frequency_mean_hz,
                frequency_min_hz,
                frequency_max_hz,
                frequency_stddev_hz,
                sample_count,
                created_at
            )
            SELECT
                series_id,
                date_bin(interval '1 hour', event_timestamp, '1970-01-01'::timestamptz),
                MAX(source_region),
                AVG(frequency_hz),
                MIN(frequency_hz),
                MAX(frequency_hz),
                STDDEV_SAMP(frequency_hz),
                COUNT(frequency_hz),
                NOW()
            FROM {_RAW_SCHEMA}.energy_charts_frequency
            WHERE event_timestamp >= %s
              AND event_timestamp < %s
            GROUP BY series_id, date_bin(interval '1 hour', event_timestamp, '1970-01-01'::timestamptz)
            ON CONFLICT (series_id, event_timestamp)
            DO UPDATE SET
                frequency_mean_hz = EXCLUDED.frequency_mean_hz,
                source_region = EXCLUDED.source_region,
                frequency_min_hz = EXCLUDED.frequency_min_hz,
                frequency_max_hz = EXCLUDED.frequency_max_hz,
                frequency_stddev_hz = EXCLUDED.frequency_stddev_hz,
                sample_count = EXCLUDED.sample_count,
                created_at = NOW()
            """,
            (start_ts, end_ts),
        )
        affected_1h = max(cursor.rowcount, 0)
    return affected_5m + affected_15m + affected_1h


def _day_row_count(series_id: str, day: datetime.date) -> int:
    day_start = datetime.datetime.combine(day, datetime.time.min, tzinfo=datetime.timezone.utc)
    day_end = day_start + datetime.timedelta(days=1)
    with _db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {_RAW_SCHEMA}.energy_charts_frequency
            WHERE series_id = %s
              AND event_timestamp >= %s
              AND event_timestamp < %s
            """,
            (series_id, day_start, day_end),
        )
        row = cursor.fetchone()
    return int(row[0]) if row else 0


def _update_state(series_id: str, last_ingested_ts: datetime.datetime | None, cursor_date: datetime.date) -> None:
    with _db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            f"""
            INSERT INTO {_RAW_SCHEMA}.energy_charts_ingestion_state (
                series_id,
                pipeline_name,
                last_ingested_ts,
                backfill_cursor_date,
                updated_at,
                status
            )
            VALUES (%s, %s, %s, %s, NOW(), %s)
            ON CONFLICT (series_id, pipeline_name)
            DO UPDATE SET
                last_ingested_ts = CASE
                    WHEN EXCLUDED.last_ingested_ts IS NULL THEN {_RAW_SCHEMA}.energy_charts_ingestion_state.last_ingested_ts
                    ELSE GREATEST({_RAW_SCHEMA}.energy_charts_ingestion_state.last_ingested_ts, EXCLUDED.last_ingested_ts)
                END,
                backfill_cursor_date = EXCLUDED.backfill_cursor_date,
                updated_at = NOW(),
                status = EXCLUDED.status
            """,
            (series_id, _PIPELINE_NAME, last_ingested_ts, cursor_date, "backfilling"),
        )
        conn.commit()


def _publish_update_event(
    *,
    series_id: str,
    window_start: datetime.datetime,
    window_end: datetime.datetime,
    rows_written: int,
) -> None:
    if rows_written <= 0:
        return

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "source": _PIPELINE_NAME,
        "pipeline": _PIPELINE_NAME,
        "series_id": series_id,
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "rows_written": rows_written,
    }
    publish_event(KafkaTopics.RAW_ENERGY_CHARTS_UPDATED.value, event)


def _default_start_date() -> datetime.date:
    return datetime.datetime.now(tz=datetime.timezone.utc).date()


def _default_end_date() -> datetime.date:
    return datetime.date(2023, 1, 1)


def _event_value(payload: dict[str, Any], key: str, default: str) -> str:
    value = payload.get(key)
    if isinstance(value, str) and value:
        return value
    return default


def _chunk_days(cursor: datetime.date, end_date: datetime.date) -> list[datetime.date]:
    days: list[datetime.date] = []
    for offset in range(_BACKFILL_CHUNK_DAYS):
        day = cursor - datetime.timedelta(days=offset)
        if day < end_date:
            break
        days.append(day)
    return days


def run_backfill(payload: dict[str, Any]) -> None:
    region = _event_value(payload, "region", os.environ.get("ENERGY_CHARTS_REGION", "DE-Freiburg"))
    start_date = _parse_date(_event_value(payload, "start_date", _default_start_date().isoformat()))
    end_date = _parse_date(_event_value(payload, "end_date", _default_end_date().isoformat()))
    request_id = _event_value(payload, "request_id", str(uuid.uuid4()))
    series_id = _series_id(region)

    logger.info(
        "Starting backfill region=%s series=%s from=%s down_to=%s",
        region,
        series_id,
        start_date,
        end_date,
    )

    cursor = start_date
    while cursor >= end_date:
        days = _chunk_days(cursor, end_date)
        if not days:
            break

        chunk_start_day = min(days)
        chunk_end_day = max(days)
        chunk_start = datetime.datetime.combine(chunk_start_day, datetime.time.min, tzinfo=datetime.timezone.utc)
        chunk_end = datetime.datetime.combine(
            chunk_end_day + datetime.timedelta(days=1),
            datetime.time.min,
            tzinfo=datetime.timezone.utc,
        )

        day_counts = {day: _day_row_count(series_id, day) for day in days}
        all_days_complete = all(count >= _MIN_COMPLETE_DAY_ROWS for count in day_counts.values())

        if all_days_complete:
            logger.info(
                "Skipping chunk %s -> %s; all %d day(s) already filled (threshold=%d)",
                chunk_start_day.isoformat(),
                chunk_end_day.isoformat(),
                len(days),
                _MIN_COMPLETE_DAY_ROWS,
            )
            written = 0
            feature_rows = 0
            max_event_ts = chunk_end - datetime.timedelta(seconds=1)
        else:
            logger.info(
                "Backfilling chunk %s -> %s; day counts=%s threshold=%d",
                chunk_start_day.isoformat(),
                chunk_end_day.isoformat(),
                {day.isoformat(): count for day, count in day_counts.items()},
                _MIN_COMPLETE_DAY_ROWS,
            )
            range_payload = collect_frequency_events_for_range(
                window_start=chunk_start,
                window_end=chunk_end,
                region=region,
                request_id=request_id,
            )
            written, max_event_ts = _upsert_rows(range_payload.get("events", []))
            with _db_connection() as conn:
                _ensure_tables(conn)
                feature_rows = _upsert_aggregates(conn, start_ts=chunk_start, end_ts=chunk_end)
                conn.commit()

        next_cursor = chunk_start_day - datetime.timedelta(days=1)
        _update_state(series_id=series_id, last_ingested_ts=max_event_ts, cursor_date=next_cursor)
        _publish_update_event(
            series_id=series_id,
            window_start=chunk_start,
            window_end=chunk_end,
            rows_written=written,
        )
        logger.info(
            "Processed chunk %s -> %s with raw_rows=%d feature_rows=%d",
            chunk_start_day.isoformat(),
            chunk_end_day.isoformat(),
            written,
            feature_rows,
        )
        cursor = next_cursor

    with _db_connection() as conn, conn.cursor() as cursor_db:
        cursor_db.execute(
            f"""
            UPDATE {_RAW_SCHEMA}.energy_charts_ingestion_state
            SET status = %s, updated_at = NOW()
            WHERE series_id = %s AND pipeline_name = %s
            """,
            ("idle", series_id, _PIPELINE_NAME),
        )
        conn.commit()


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    topic = os.environ.get("KAFKA_TOPIC", KafkaTopics.CMD_ENERGY_CHARTS_BACKFILL.value)

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=os.environ.get("KAFKA_CONSUMER_GROUP", "energy-charts-backfill-service"),
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    logger.info("Backfill service listening on topic '%s'", topic)
    try:
        for message in consumer:
            payload = message.value if isinstance(message.value, dict) else {}
            try:
                run_backfill(payload)
            except Exception:
                logger.exception("Backfill run failed")
    finally:
        consumer.close()


if __name__ == "__main__":
    run()
