"""Ingest raw energy-charts frequency events and build Feast features."""

from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Any, Dict, Iterable, List

import psycopg
from airflow.decorators import dag, task
from kafka import KafkaConsumer
from kafka.structs import OffsetAndMetadata, TopicPartition

from shared.kafka.topics import KafkaTopics

logger = logging.getLogger(__name__)


_RAW_SCHEMA = os.environ.get("RAW_SCHEMA", "raw")
_FEAST_SCHEMA = os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")
_MAX_MESSAGES = int(os.environ.get("ENERGY_CHARTS_MAX_MESSAGES", "5000"))
_CONSUMER_TIMEOUT_MS = int(os.environ.get("ENERGY_CHARTS_CONSUMER_TIMEOUT_MS", "1000"))


def _db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["FEAST_OFFLINE_STORE_HOST"],
        port=int(os.environ.get("FEAST_OFFLINE_STORE_PORT", "5432")),
        dbname=os.environ["FEAST_OFFLINE_STORE_DATABASE"],
        user=os.environ["FEAST_OFFLINE_STORE_USER"],
        password=os.environ["FEAST_OFFLINE_STORE_PASSWORD"],
    )


def _ensure_raw_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_RAW_SCHEMA}")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_RAW_SCHEMA}.energy_charts_frequency (
                event_id TEXT PRIMARY KEY,
                series_id TEXT NOT NULL,
                event_timestamp TIMESTAMPTZ NOT NULL,
                frequency_hz DOUBLE PRECISION NULL,
                source_region TEXT NOT NULL,
                request_id TEXT NOT NULL,
                collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
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
            f"""
            CREATE INDEX IF NOT EXISTS idx_raw_energy_charts_frequency_series_ts
            ON {_RAW_SCHEMA}.energy_charts_frequency (series_id, event_timestamp)
            """
        )


def _ensure_feature_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {_FEAST_SCHEMA}")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {_FEAST_SCHEMA}.grid_frequency_5m (
                series_id TEXT NOT NULL,
                event_timestamp TIMESTAMPTZ NOT NULL,
                frequency_hz DOUBLE PRECISION NULL,
                source_region TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (series_id, event_timestamp)
            )
            """
        )
        cursor.execute(
            f"""
            CREATE INDEX IF NOT EXISTS ix_grid_frequency_5m_event_timestamp
            ON {_FEAST_SCHEMA}.grid_frequency_5m (event_timestamp)
            """
        )


def _parse_iso_ts(value: str) -> datetime.datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _dedupe_events(events: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for event in events:
        event_id = event.get("event_id")
        if not event_id or event_id in seen:
            continue
        seen.add(event_id)
        unique.append(event)
    return unique


@dag(
    dag_id="energy_charts_pipeline",
    description="Consume raw energy-charts events and build Feast features.",
    schedule="*/5 * * * *",
    start_date=datetime.datetime(2026, 3, 13),
    catchup=False,
    tags=["energy-charts"],
)
def energy_charts_pipeline() -> None:
    @task()
    def consume_raw_events() -> Dict[str, Any]:
        bootstrap = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
        consumer = KafkaConsumer(
            KafkaTopics.RAW_ENERGY_CHARTS.value,
            bootstrap_servers=bootstrap,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            group_id="energy-charts-pipeline",
            consumer_timeout_ms=_CONSUMER_TIMEOUT_MS,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )

        events: List[Dict[str, Any]] = []
        offsets: Dict[tuple[str, int], int] = {}

        try:
            for message in consumer:
                events.append(message.value)
                offsets[(message.topic, message.partition)] = message.offset + 1
                if len(events) >= _MAX_MESSAGES:
                    break
        finally:
            consumer.close()

        logger.info("Consumed %d raw events", len(events))
        return {
            "events": events,
            "offsets": [
                {"topic": topic, "partition": partition, "offset": offset}
                for (topic, partition), offset in offsets.items()
            ],
        }

    @task()
    def write_raw_table(payload: Dict[str, Any]) -> Dict[str, Any]:
        events = _dedupe_events(payload.get("events", []))
        payload["events"] = events
        if not events:
            payload["written"] = False
            return payload

        with _db_connection() as conn:
            _ensure_raw_table(conn)
            with conn.cursor() as cursor:
                rows = [
                    (
                        event["event_id"],
                        event["series_id"],
                        _parse_iso_ts(event["event_timestamp"]),
                        event.get("frequency_hz"),
                        event["source_region"],
                        event["request_id"],
                        _parse_iso_ts(event["collected_at"]),
                    )
                    for event in events
                ]
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
                    ON CONFLICT DO NOTHING
                    """,
                    rows,
                )
            conn.commit()

        payload["written"] = True
        return payload

    @task()
    def aggregate_to_features(payload: Dict[str, Any]) -> Dict[str, Any]:
        if not payload.get("written"):
            return payload

        events = payload.get("events", [])
        if not events:
            return payload

        timestamps = [_parse_iso_ts(event["event_timestamp"]) for event in events]
        window_start = min(timestamps)
        window_end = max(timestamps) + datetime.timedelta(seconds=1)

        with _db_connection() as conn:
            _ensure_feature_table(conn)
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {_FEAST_SCHEMA}.grid_frequency_5m (
                        series_id,
                        event_timestamp,
                        frequency_hz,
                        source_region,
                        created_at
                    )
                    SELECT
                        series_id,
                        date_trunc('hour', event_timestamp)
                            + interval '5 min' * floor(extract(minute from event_timestamp) / 5),
                        AVG(frequency_hz) AS frequency_hz,
                        MAX(source_region) AS source_region,
                        NOW() AS created_at
                    FROM {_RAW_SCHEMA}.energy_charts_frequency
                    WHERE event_timestamp >= %s
                      AND event_timestamp < %s
                    GROUP BY series_id, date_trunc('hour', event_timestamp)
                             + interval '5 min' * floor(extract(minute from event_timestamp) / 5)
                    ON CONFLICT (series_id, event_timestamp)
                    DO UPDATE SET
                        frequency_hz = EXCLUDED.frequency_hz,
                        source_region = EXCLUDED.source_region,
                        created_at = NOW()
                    """,
                    (window_start, window_end),
                )
            conn.commit()

        return payload

    @task()
    def commit_offsets(payload: Dict[str, Any]) -> None:
        if not payload.get("written"):
            logger.info("Skipping offset commit; no events written.")
            return

        offsets = payload.get("offsets", [])
        if not offsets:
            logger.info("Skipping offset commit; no offsets.")
            return

        bootstrap = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
        consumer = KafkaConsumer(
            KafkaTopics.RAW_ENERGY_CHARTS.value,
            bootstrap_servers=bootstrap,
            enable_auto_commit=False,
            group_id="energy-charts-pipeline",
        )
        try:
            commit_map = {
                TopicPartition(entry["topic"], entry["partition"]): OffsetAndMetadata(
                    entry["offset"],
                    None,
                    -1,
                )
                for entry in offsets
            }
            consumer.commit(offsets=commit_map)
            logger.info("Committed offsets for %d partitions", len(commit_map))
        finally:
            consumer.close()

    payload = consume_raw_events()
    payload = write_raw_table(payload)
    payload = aggregate_to_features(payload)
    commit_offsets(payload)


energy_charts_pipeline()
