from __future__ import annotations

import datetime

from shared.energy_charts.backfill import chunk_days, resolve_backfill_command
from shared.energy_charts.events import build_raw_update_event, normalize_events
from shared.energy_charts.series import series_id_for_region
from shared.energy_charts.time import parse_iso_timestamp


def test_parse_iso_timestamp_normalizes_utc() -> None:
    parsed = parse_iso_timestamp("2026-03-14T12:00:00Z")
    assert parsed == datetime.datetime(2026, 3, 14, 12, 0, tzinfo=datetime.timezone.utc)


def test_series_id_for_region_is_normalized() -> None:
    assert series_id_for_region("DE-Freiburg") == "de-freiburg::grid_frequency"


def test_normalize_events_converts_payload_to_records() -> None:
    records = normalize_events([
        {
            "event_id": "event-1",
            "series_id": "de-freiburg::grid_frequency",
            "event_timestamp": "2026-03-14T12:00:00Z",
            "frequency_hz": 49.98,
            "source_region": "DE-Freiburg",
            "request_id": "req-1",
            "collected_at": "2026-03-14T12:00:01Z",
        }
    ])

    assert len(records) == 1
    assert records[0].event_timestamp == datetime.datetime(2026, 3, 14, 12, 0, tzinfo=datetime.timezone.utc)


def test_build_raw_update_event_contains_required_fields() -> None:
    event = build_raw_update_event(
        pipeline_name="pipeline",
        series_id="de-freiburg::grid_frequency",
        window_start="2026-03-14T12:00:00+00:00",
        window_end="2026-03-14T12:05:00+00:00",
        rows_written=42,
    )

    assert event["pipeline"] == "pipeline"
    assert event["rows_written"] == 42
    assert event["series_id"] == "de-freiburg::grid_frequency"


def test_resolve_backfill_command_validates_date_order() -> None:
    command = resolve_backfill_command(
        {"region": "DE-Freiburg", "start_date": "2026-03-14", "end_date": "2026-03-01", "request_id": "req-1"},
        default_region="DE-Freiburg",
    )

    assert command.request_id == "req-1"
    assert command.start_date == datetime.date(2026, 3, 14)
    assert command.end_date == datetime.date(2026, 3, 1)


def test_chunk_days_stops_at_end_date() -> None:
    days = chunk_days(datetime.date(2026, 3, 14), datetime.date(2026, 3, 12), chunk_size=4)
    assert days == [datetime.date(2026, 3, 14), datetime.date(2026, 3, 13), datetime.date(2026, 3, 12)]
