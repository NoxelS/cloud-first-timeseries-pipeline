"""Incrementally ingest second-level Energy Charts frequency data into Postgres."""

from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

from airflow.sdk import dag, task

from shared.adapters.energy_charts.collector import collect_frequency_events_for_range
from shared.config import EnergyChartsSettings, load_energy_charts_settings
from shared.db.repositories import get_ingestion_state, upsert_frequency_events, upsert_ingestion_state
from shared.db.session import session_scope
from shared.energy_charts.events import RawWindowPayload, build_raw_update_event, normalize_events
from shared.energy_charts.series import series_id_for_region
from shared.energy_charts.time import parse_iso_timestamp, utc_now
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics

logger = logging.getLogger(__name__)

_PIPELINE_NAME = "energy-charts-feature-pipeline"


def _settings() -> EnergyChartsSettings:
    return load_energy_charts_settings()


@dag(
    dag_id="energy-charts-feature-pipeline",
    description="Incremental raw frequency ingestion with cursor-based windows.",
    schedule="*/5 * * * *",
    start_date=datetime.datetime(2026, 3, 13, tzinfo=datetime.timezone.utc),
    catchup=False,
    tags=["energy-charts", "raw"],
)
def energy_charts_feature_pipeline() -> None:  # noqa: C901
    @task()
    def prepare_window() -> dict[str, Any]:
        settings = _settings()
        region = settings.region
        series_id = series_id_for_region(region)
        # Keep a small safety lag so we do not ingest points still being published upstream.
        window_end = utc_now() - datetime.timedelta(seconds=settings.safety_lag_seconds)

        with session_scope() as session:
            state = get_ingestion_state(session, series_id=series_id, pipeline_name=_PIPELINE_NAME)

        if state and state.last_ingested_ts:
            last_ingested_ts = state.last_ingested_ts.astimezone(datetime.timezone.utc)
            # Re-read a small overlap window to tolerate late-arriving or corrected samples.
            window_start = last_ingested_ts - datetime.timedelta(seconds=settings.overlap_seconds)
        else:
            window_start = window_end - datetime.timedelta(hours=settings.initial_lookback_hours)

        if window_start >= window_end:
            window_start = window_end - datetime.timedelta(minutes=1)

        return RawWindowPayload(
            request_id=str(uuid.uuid4()),
            region=region,
            series_id=series_id,
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
        ).__dict__

    @task()
    def collect_raw_events(window: dict[str, Any]) -> dict[str, Any]:
        payload = collect_frequency_events_for_range(
            window_start=parse_iso_timestamp(window["window_start"]),
            window_end=parse_iso_timestamp(window["window_end"]),
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
            payload["max_event_timestamp"] = None
            return payload

        with session_scope() as session:
            result = upsert_frequency_events(session, normalize_events(events))

        payload["rows_written"] = result.rows_written
        payload["max_event_timestamp"] = result.max_event_timestamp.isoformat() if result.max_event_timestamp else None
        return payload

    @task()
    def update_ingestion_state(payload: dict[str, Any]) -> dict[str, Any]:
        max_event_ts = payload.get("max_event_timestamp")
        if not max_event_ts:
            logger.info("No max event timestamp; ingestion cursor remains unchanged.")
            return payload

        with session_scope() as session:
            upsert_ingestion_state(
                session,
                series_id=payload["series_id"],
                pipeline_name=_PIPELINE_NAME,
                last_ingested_ts=parse_iso_timestamp(max_event_ts),
                backfill_cursor_date=None,
                status="live",
            )
        return payload

    @task()
    def publish_raw_update_trigger(payload: dict[str, Any]) -> None:
        if payload.get("rows_written", 0) <= 0:
            logger.info("Skipping raw update trigger; no rows written.")
            return

        event = build_raw_update_event(
            pipeline_name=_PIPELINE_NAME,
            series_id=payload["series_id"],
            window_start=payload["window_start"],
            window_end=payload["window_end"],
            rows_written=payload["rows_written"],
        )
        publish_event(KafkaTopics.RAW_ENERGY_CHARTS_UPDATED.value, event)

    window = prepare_window()
    payload = collect_raw_events(window)
    payload = write_raw_table(payload)
    payload = update_ingestion_state(payload)
    publish_raw_update_trigger(payload)


energy_charts_feature_pipeline()
