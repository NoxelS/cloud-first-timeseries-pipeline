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
_WINDOW_MINUTES = 5
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


def parse_command_timestamp(command: dict[str, Any]) -> datetime.datetime:
    raw_ts = command.get("timestamp")
    if not raw_ts:
        return datetime.datetime.now(tz=datetime.timezone.utc)

    if isinstance(raw_ts, str):
        try:
            return _parse_iso_ts(raw_ts)
        except ValueError:
            logger.warning("Invalid command timestamp '%s', falling back to now()", raw_ts)
            return datetime.datetime.now(tz=datetime.timezone.utc)

    logger.warning("Unsupported timestamp type '%s', falling back to now()", type(raw_ts))
    return datetime.datetime.now(tz=datetime.timezone.utc)


def window_bounds(end_ts: datetime.datetime) -> tuple[datetime.datetime, datetime.datetime]:
    start_ts = end_ts - datetime.timedelta(minutes=_WINDOW_MINUTES)
    return start_ts, end_ts


def _zip_points(unix_seconds: list[int], values: list[float | None]) -> list[tuple[int, float | None]]:
    if len(unix_seconds) != len(values):
        logger.warning(
            "Frequency response length mismatch: unix_seconds=%d values=%d. Truncating to min length.",
            len(unix_seconds),
            len(values),
        )
    return list(zip(unix_seconds, values, strict=False))


def fetch_frequency_points(*, region: str, start_date: str, end_date: str) -> tuple[list[int], list[float | None]]:
    params = urlencode({"region": region, "start": start_date, "end": end_date})
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

    for second, value in _zip_points(unix_seconds, values):
        point_ts = datetime.datetime.fromtimestamp(second, tz=datetime.timezone.utc)
        if point_ts < window_start or point_ts >= window_end:
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


def collect_frequency_events(command: dict[str, Any]) -> dict[str, Any]:
    region = command.get("region", _DEFAULT_REGION)
    request_id = command.get("request_id", str(uuid.uuid4()))
    end_ts = parse_command_timestamp(command)
    window_start, window_end = window_bounds(end_ts)

    start_date = window_start.date().isoformat()
    end_date = window_end.date().isoformat()
    unix_seconds, frequencies = fetch_frequency_points(region=region, start_date=start_date, end_date=end_date)

    collected_at = datetime.datetime.now(tz=datetime.timezone.utc)
    events = build_raw_events(
        unix_seconds=unix_seconds,
        values=frequencies,
        region=region,
        request_id=request_id,
        window_start=window_start,
        window_end=window_end,
        collected_at=collected_at,
    )

    return {
        "events": events,
        "request_id": request_id,
        "source_region": region,
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
    }
