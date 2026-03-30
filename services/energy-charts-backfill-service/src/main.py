from __future__ import annotations

import datetime
import logging
from typing import Any

from shared.adapters.energy_charts.collector import collect_frequency_events_for_range
from shared.config import EnergyChartsSettings, load_energy_charts_settings
from shared.db.repositories import day_row_count, set_ingestion_status, upsert_frequency_events, upsert_ingestion_state
from shared.db.session import session_scope
from shared.energy_charts.backfill import BackfillCommand, chunk_days, resolve_backfill_command
from shared.energy_charts.events import build_raw_update_event, normalize_events
from shared.energy_charts.series import series_id_for_region
from shared.energy_charts.time import utc_now
from shared.kafka.consumer import create_json_consumer
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics

logger = logging.getLogger(__name__)

_PIPELINE_NAME = "energy-charts-backfill-service"


def _settings() -> EnergyChartsSettings:
    return load_energy_charts_settings()


def _publish_update_event(
    *,
    series_id: str,
    window_start: datetime.datetime,
    window_end: datetime.datetime,
    rows_written: int,
) -> None:
    if rows_written <= 0:
        return

    event = build_raw_update_event(
        pipeline_name=_PIPELINE_NAME,
        series_id=series_id,
        window_start=window_start.isoformat(),
        window_end=window_end.isoformat(),
        rows_written=rows_written,
    )
    publish_event(KafkaTopics.RAW_ENERGY_CHARTS_UPDATED.value, event)


def _default_start_date() -> datetime.date:
    return utc_now().date()


def _default_end_date() -> datetime.date:
    return datetime.date(2023, 1, 1)


def run_backfill(payload: dict[str, Any]) -> None:
    settings = _settings()
    command = resolve_backfill_command(
        payload,
        default_region=settings.region,
        default_start_date=_default_start_date(),
        default_end_date=_default_end_date(),
    )
    _run_backfill_command(command)


def _run_backfill_command(command: BackfillCommand) -> None:
    series_id = series_id_for_region(command.region)

    logger.info(
        "Starting backfill region=%s series=%s from=%s down_to=%s",
        command.region,
        series_id,
        command.start_date,
        command.end_date,
    )

    cursor = command.start_date
    while cursor >= command.end_date:
        days = chunk_days(cursor, command.end_date, chunk_size=_settings().backfill_chunk_days)
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

        with session_scope() as session:
            day_counts = {day: day_row_count(session, series_id=series_id, day=day) for day in days}
        all_days_complete = all(count >= _settings().backfill_min_complete_day_rows for count in day_counts.values())

        if all_days_complete:
            logger.info(
                "Skipping chunk %s -> %s; all %d day(s) already filled (threshold=%d)",
                chunk_start_day.isoformat(),
                chunk_end_day.isoformat(),
                len(days),
                _settings().backfill_min_complete_day_rows,
            )
            written = 0
            max_event_ts = chunk_end - datetime.timedelta(seconds=1)
        else:
            logger.info(
                "Backfilling chunk %s -> %s; day counts=%s threshold=%d",
                chunk_start_day.isoformat(),
                chunk_end_day.isoformat(),
                {day.isoformat(): count for day, count in day_counts.items()},
                _settings().backfill_min_complete_day_rows,
            )
            range_payload = collect_frequency_events_for_range(
                window_start=chunk_start,
                window_end=chunk_end,
                region=command.region,
                request_id=command.request_id,
            )
            with session_scope() as session:
                result = upsert_frequency_events(session, normalize_events(range_payload.get("events", [])))
            written = result.rows_written
            max_event_ts = result.max_event_timestamp

        next_cursor = chunk_start_day - datetime.timedelta(days=1)
        with session_scope() as session:
            upsert_ingestion_state(
                session,
                series_id=series_id,
                pipeline_name=_PIPELINE_NAME,
                last_ingested_ts=max_event_ts,
                backfill_cursor_date=next_cursor,
                status="backfilling",
            )
        _publish_update_event(
            series_id=series_id,
            window_start=chunk_start,
            window_end=chunk_end,
            rows_written=written,
        )
        logger.info(
            "Processed chunk %s -> %s with raw_rows=%d",
            chunk_start_day.isoformat(),
            chunk_end_day.isoformat(),
            written,
        )
        cursor = next_cursor

    with session_scope() as session:
        set_ingestion_status(session, series_id=series_id, pipeline_name=_PIPELINE_NAME, status="idle")


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    topic = KafkaTopics.CMD_ENERGY_CHARTS_BACKFILL.value

    consumer = create_json_consumer(
        topic,
        group_id="energy-charts-backfill-service",
        auto_offset_reset="latest",
        enable_auto_commit=False,
    )

    logger.info("Backfill service listening on topic '%s'", topic)
    try:
        for message in consumer:
            payload = message.value if isinstance(message.value, dict) else {}
            try:
                run_backfill(payload)
                consumer.commit()
            except Exception:
                logger.exception("Backfill run failed")
    finally:
        consumer.close()


if __name__ == "__main__":
    run()
