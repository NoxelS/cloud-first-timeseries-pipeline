"""Time helpers for Energy Charts ingestion flows."""

from __future__ import annotations

import datetime


def parse_iso_timestamp(value: str) -> datetime.datetime:
    """Parse an ISO timestamp and normalize it to UTC."""
    parsed = value.replace("Z", "+00:00") if value.endswith("Z") else value
    dt = datetime.datetime.fromisoformat(parsed)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)
