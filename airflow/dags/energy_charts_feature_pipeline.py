"""Collect Energy Charts frequency data, build features, materialize, and emit training triggers."""

# ruff: noqa: S608

from __future__ import annotations

import datetime
import logging
import os
import uuid
from typing import Any

import psycopg
from airflow.decorators import dag, task

from shared.adapters.energy_charts.collector import collect_frequency_events
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics

logger = logging.getLogger(__name__)


_RAW_SCHEMA = os.environ.get("RAW_SCHEMA", "raw")
_FEAST_SCHEMA = os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")
_FEAST_REPO_PATH = os.environ.get("FEAST_REPO_PATH", "/opt/airflow/feast/feature_repo")
_ENABLE_MATERIALIZATION = os.environ.get("ENABLE_FEAST_MATERIALIZATION", "false").lower() == "true"


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


@dag(
    dag_id="energy-charts-feature-pipeline",
    description="Collect frequency data, build features, materialize, and trigger model training.",
    schedule="*/5 * * * *",
    start_date=datetime.datetime(2026, 3, 13),
    catchup=False,
    tags=["energy-charts"],
)
def energy_charts_feature_pipeline() -> None:  # noqa: C901
    @task()
    def collect_raw_events() -> dict[str, Any]:
        command = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            "region": os.environ.get("ENERGY_CHARTS_REGION", "DE-Freiburg"),
        }
        payload = collect_frequency_events(command)
        logger.info("Collected %d raw frequency events", len(payload.get("events", [])))
        return payload

    @task()
    def write_raw_table(payload: dict[str, Any]) -> dict[str, Any]:
        events = payload.get("events", [])
        if not events:
            payload["written_raw"] = False
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

        payload["written_raw"] = True
        return payload

    @task()
    def aggregate_to_features(payload: dict[str, Any]) -> dict[str, Any]:
        if not payload.get("written_raw"):
            payload["affected_feature_rows"] = 0
            return payload

        window_start = _parse_iso_ts(payload["window_start"])
        window_end = _parse_iso_ts(payload["window_end"])

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
                    WHERE {_FEAST_SCHEMA}.grid_frequency_5m.frequency_hz IS DISTINCT FROM EXCLUDED.frequency_hz
                       OR {_FEAST_SCHEMA}.grid_frequency_5m.source_region IS DISTINCT FROM EXCLUDED.source_region
                    """,
                    (window_start, window_end),
                )
                affected_rows = cursor.rowcount
            conn.commit()

        payload["affected_feature_rows"] = max(affected_rows, 0)
        logger.info("Affected %d feature rows", payload["affected_feature_rows"])
        return payload

    @task()
    def materialize_features(payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("affected_feature_rows", 0) <= 0:
            payload["materialized"] = False
            return payload

        if not _ENABLE_MATERIALIZATION:
            logger.info("Skipping Feast materialization because ENABLE_FEAST_MATERIALIZATION is false.")
            payload["materialized"] = False
            return payload

        try:
            from feast import FeatureStore
        except ImportError:
            logger.warning("Skipping Feast materialization because Feast is not installed in Airflow runtime.")
            payload["materialized"] = False
            return payload

        window_end = _parse_iso_ts(payload["window_end"])
        store = FeatureStore(repo_path=_FEAST_REPO_PATH)
        store.materialize_incremental(end_date=window_end)
        payload["materialized"] = True
        return payload

    @task()
    def publish_training_trigger(payload: dict[str, Any]) -> None:
        if not payload.get("materialized"):
            logger.info("Skipping training trigger; no new feature data was materialized.")
            return

        events = payload.get("events", [])
        series_id = events[0]["series_id"] if events else None
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            "source": "energy-charts-feature-pipeline",
            "pipeline": "energy-charts-feature-pipeline",
            "window_start": payload["window_start"],
            "window_end": payload["window_end"],
            "series_id": series_id,
            "affected_feature_rows": payload.get("affected_feature_rows", 0),
            "materialized": True,
        }
        publish_event(KafkaTopics.CMD_MODEL_TRAINING.value, event)
        logger.info("Published training trigger event to %s", KafkaTopics.CMD_MODEL_TRAINING.value)

    payload = collect_raw_events()
    payload = write_raw_table(payload)
    payload = aggregate_to_features(payload)
    payload = materialize_features(payload)
    publish_training_trigger(payload)


energy_charts_feature_pipeline()
