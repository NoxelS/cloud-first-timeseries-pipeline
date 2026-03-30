"""Typed event helpers for raw Energy Charts ingestion."""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from typing import Any

from shared.energy_charts.time import parse_iso_timestamp, utc_now
from shared.schemas import RawUpdatePayload


@dataclass(frozen=True)
class FrequencyRecord:
    event_id: str
    series_id: str
    event_timestamp: datetime.datetime
    frequency_hz: float | None
    source_region: str
    request_id: str
    collected_at: datetime.datetime


@dataclass(frozen=True)
class RawWindowPayload:
    request_id: str
    region: str
    series_id: str
    window_start: str
    window_end: str


def normalize_events(events: list[dict[str, Any]]) -> list[FrequencyRecord]:
    """Convert collector payloads into typed DB records."""
    return [
        FrequencyRecord(
            event_id=event["event_id"],
            series_id=event["series_id"],
            event_timestamp=parse_iso_timestamp(event["event_timestamp"]),
            frequency_hz=event.get("frequency_hz"),
            source_region=event["source_region"],
            request_id=event["request_id"],
            collected_at=parse_iso_timestamp(event["collected_at"]),
        )
        for event in events
    ]


def build_raw_update_event(
    *,
    pipeline_name: str,
    series_id: str,
    window_start: str,
    window_end: str,
    rows_written: int,
) -> dict[str, Any]:
    return RawUpdatePayload(
        event_id=str(uuid.uuid4()),
        timestamp=utc_now().isoformat(),
        source=pipeline_name,
        pipeline=pipeline_name,
        series_id=series_id,
        window_start=window_start,
        window_end=window_end,
        rows_written=rows_written,
    ).to_dict()
