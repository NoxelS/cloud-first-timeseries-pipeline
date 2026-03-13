from __future__ import annotations

import datetime
import json
import logging
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.energy-charts.info/frequency"
_DEFAULT_REGION = "DE-Freiburg"
_REQUEST_TIMEOUT_SECONDS = 30


def _parse_iso_ts(value: str) -> datetime.datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    parsed = datetime.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _make_series_id(country: str, production_type: str) -> str:
    return f"{country}::{production_type}"


def _coerce_utc(value: datetime.datetime) -> datetime.datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


def _zip_points(unix_seconds: list[int], values: list[float | None]) -> list[tuple[int, float | None]]:
    if len(unix_seconds) != len(values):
        logger.warning(
            "Frequency response length mismatch: unix_seconds=%d values=%d. Truncating to min length.",
            len(unix_seconds),
            len(values),
        )
    return list(zip(unix_seconds, values, strict=False))


def fetch_frequency_points(*, region: str, start: str, end: str) -> tuple[list[int], list[float | None]]:
    params = urlencode({"region": region, "start": start, "end": end})
    url = f"{_BASE_URL}?{params}"
    try:
        with urlopen(url, timeout=_REQUEST_TIMEOUT_SECONDS) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        logger.warning("Energy Charts API returned HTTP %s for %s", exc.code, url)
        return [], []
    except URLError as exc:
        logger.warning("Energy Charts API request failed for %s: %s", url, exc)
        return [], []

    unix_seconds = payload.get("unix_seconds") or []
    data = payload.get("data") or []
    if not isinstance(unix_seconds, list) or not isinstance(data, list):
        logger.warning("Unexpected Energy Charts response payload shape")
        return [], []

    return unix_seconds, data


def build_raw_events(
    *,
    unix_seconds: list[int],
    values: list[float | None],
    region: str,
    request_id: str,
    window_start: datetime.datetime,
    window_end: datetime.datetime,
    collected_at: datetime.datetime,
) -> list[dict[str, Any]]:
    series = _make_series_id(region.lower(), "grid_frequency")
    events: list[dict[str, Any]] = []

    start_utc = _coerce_utc(window_start)
    end_utc = _coerce_utc(window_end)

    for second, value in _zip_points(unix_seconds, values):
        point_ts = datetime.datetime.fromtimestamp(second, tz=datetime.timezone.utc)
        if point_ts < start_utc or point_ts >= end_utc:
            continue
        event_fingerprint = f"{series}:{point_ts.isoformat()}"
        events.append({
            "event_id": str(uuid.uuid5(uuid.NAMESPACE_URL, event_fingerprint)),
            "request_id": request_id,
            "series_id": series,
            "source_region": region,
            "event_timestamp": point_ts.isoformat(),
            "frequency_hz": value,
            "collected_at": collected_at.isoformat(),
        })

    return events


def collect_frequency_events_for_range(
    *,
    window_start: datetime.datetime,
    window_end: datetime.datetime,
    region: str = _DEFAULT_REGION,
    request_id: str | None = None,
) -> dict[str, Any]:
    start_utc = _coerce_utc(window_start)
    end_utc = _coerce_utc(window_end)
    request = request_id or str(uuid.uuid4())

    if start_utc >= end_utc:
        return {
            "events": [],
            "request_id": request,
            "source_region": region,
            "window_start": start_utc.isoformat(),
            "window_end": end_utc.isoformat(),
        }

    events: list[dict[str, Any]] = []
    day = start_utc.date()
    final_day = (end_utc - datetime.timedelta(microseconds=1)).date()
    collected_at = datetime.datetime.now(tz=datetime.timezone.utc)

    while day <= final_day:
        day_start = datetime.datetime.combine(day, datetime.time.min, tzinfo=datetime.timezone.utc)
        day_end = day_start + datetime.timedelta(days=1)
        slice_start = max(start_utc, day_start)
        slice_end = min(end_utc, day_end)
        start_unix = int(slice_start.timestamp())
        end_unix = int(slice_end.timestamp()) - 1
        if start_unix > end_unix:
            day += datetime.timedelta(days=1)
            continue

        unix_seconds, frequencies = fetch_frequency_points(
            region=region,
            start=str(start_unix),
            end=str(end_unix),
        )
        events.extend(
            build_raw_events(
                unix_seconds=unix_seconds,
                values=frequencies,
                region=region,
                request_id=request,
                window_start=start_utc,
                window_end=end_utc,
                collected_at=collected_at,
            )
        )
        day += datetime.timedelta(days=1)

    return {
        "events": events,
        "request_id": request,
        "source_region": region,
        "window_start": start_utc.isoformat(),
        "window_end": end_utc.isoformat(),
    }


def collect_frequency_events_for_day(
    *,
    day: datetime.date,
    region: str = _DEFAULT_REGION,
    request_id: str | None = None,
) -> dict[str, Any]:
    day_start = datetime.datetime.combine(day, datetime.time.min, tzinfo=datetime.timezone.utc)
    day_end = day_start + datetime.timedelta(days=1)
    return collect_frequency_events_for_range(
        window_start=day_start,
        window_end=day_end,
        region=region,
        request_id=request_id,
    )
