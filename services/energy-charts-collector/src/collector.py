from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any, Dict, Iterable, List, Tuple

from schema import make_series_id
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics

from energy_charts_api_client import Client
from energy_charts_api_client.models.http_validation_error import HTTPValidationError

logger = logging.getLogger(__name__)


_DEFAULT_REGION = "DE-Freiburg"
_WINDOW_MINUTES = 5


def _parse_command_timestamp(command: Dict[str, Any]) -> datetime.datetime:
    raw_ts = command.get("timestamp")
    if not raw_ts:
        return datetime.datetime.now(tz=datetime.timezone.utc)

    if isinstance(raw_ts, str):
        if raw_ts.endswith("Z"):
            raw_ts = raw_ts.replace("Z", "+00:00")
        try:
            parsed = datetime.datetime.fromisoformat(raw_ts)
        except ValueError:
            logger.warning("Invalid command timestamp '%s', falling back to now()", raw_ts)
            return datetime.datetime.now(tz=datetime.timezone.utc)
    else:
        logger.warning("Unsupported timestamp type '%s', falling back to now()", type(raw_ts))
        return datetime.datetime.now(tz=datetime.timezone.utc)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _window_bounds(end_ts: datetime.datetime) -> Tuple[datetime.datetime, datetime.datetime]:
    start_ts = end_ts - datetime.timedelta(minutes=_WINDOW_MINUTES)
    return start_ts, end_ts


def _zip_points(
    unix_seconds: Iterable[int],
    values: Iterable[float | None],
) -> Iterable[Tuple[int, float | None]]:
    unix_list = list(unix_seconds)
    values_list = list(values)
    if len(unix_list) != len(values_list):
        logger.warning(
            "Frequency response length mismatch: unix_seconds=%d values=%d. Truncating to min length.",
            len(unix_list),
            len(values_list),
        )
    return zip(unix_list, values_list)


def build_raw_events(
    *,
    unix_seconds: List[int],
    values: List[float | None],
    region: str,
    request_id: str,
    window_start: datetime.datetime,
    window_end: datetime.datetime,
    collected_at: datetime.datetime,
) -> List[Dict[str, Any]]:
    series = make_series_id(region.lower(), "grid_frequency")
    events: List[Dict[str, Any]] = []
    for second, value in _zip_points(unix_seconds, values):
        point_ts = datetime.datetime.fromtimestamp(second, tz=datetime.timezone.utc)
        if point_ts < window_start or point_ts >= window_end:
            continue
        events.append(
            {
                "event_id": str(uuid.uuid4()),
                "request_id": request_id,
                "series_id": series,
                "source_region": region,
                "event_timestamp": point_ts.isoformat(),
                "frequency_hz": value,
                "collected_at": collected_at.isoformat(),
            }
        )
    return events


def handle_collection_command(command: Dict[str, Any], *, countries: List[str] | None = None) -> int:
    """Handle an incoming collection command: fetch and publish events.

    Returns number of published events.
    """
    logger.info("Handling collection command: %s", command)

    client = Client(base_url="https://api.energy-charts.info")
    region = command.get("region", _DEFAULT_REGION)
    request_id = command.get("request_id", str(uuid.uuid4()))
    end_ts = _parse_command_timestamp(command)
    window_start, window_end = _window_bounds(end_ts)
    start_date = window_start.date().isoformat()
    end_date = window_end.date().isoformat()

    with client as client:
        from energy_charts_api_client.api.power.frequency_frequency_get import sync as get_frequency

        logger.info(
            "Fetching frequency window start=%s end=%s region=%s",
            window_start.isoformat(),
            window_end.isoformat(),
            region,
        )

        response = get_frequency(client=client, region=region, start=start_date, end=end_date)
        if isinstance(response, HTTPValidationError):
            logger.warning("Frequency response validation error: %s", response.to_dict())
            return 0
        if response is None:
            logger.warning("Frequency response is empty")
            return 0

        unix_seconds = response.unix_seconds or []
        frequencies = response.data or []
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

        logger.info("Fetched %d frequency points and produced %d raw events", len(frequencies), len(events))
        if not events:
            return 0

        for event in events:
            publish_event(KafkaTopics.RAW_ENERGY_CHARTS.value, event)

        logger.info(
            "Published raw frequency events range: %s to %s",
            events[0]["event_timestamp"],
            events[-1]["event_timestamp"],
        )

        return len(events)



if __name__ == "__main__":
    # Simple CLI entry for manual runs or Docker CMD
    cmd = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "datasets": "all",
    }
    print("Handling collection command (manual run)...")
    n = handle_collection_command(cmd)
    print(f"Published {n} events")
