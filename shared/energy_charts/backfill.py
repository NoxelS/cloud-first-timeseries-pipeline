"""Backfill planning helpers."""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass

from shared.energy_charts.time import utc_now

DEFAULT_BACKFILL_END_DATE = datetime.date(2023, 1, 1)


@dataclass(frozen=True)
class BackfillCommand:
    region: str
    start_date: datetime.date
    end_date: datetime.date
    request_id: str


def resolve_backfill_command(
    payload: dict[str, object],
    *,
    default_region: str,
    default_start_date: datetime.date | None = None,
    default_end_date: datetime.date = DEFAULT_BACKFILL_END_DATE,
) -> BackfillCommand:
    start_date = _parse_date_value(payload.get("start_date"), default_start_date or utc_now().date())
    end_date = _parse_date_value(payload.get("end_date"), default_end_date)
    if start_date < end_date:
        raise ValueError(  # noqa: TRY003
            f"start_date {start_date.isoformat()} must be on or after end_date {end_date.isoformat()}"
        )

    return BackfillCommand(
        region=_string_value(payload.get("region"), default_region),
        start_date=start_date,
        end_date=end_date,
        request_id=_string_value(payload.get("request_id"), str(uuid.uuid4())),
    )


def chunk_days(cursor: datetime.date, end_date: datetime.date, *, chunk_size: int) -> list[datetime.date]:
    days: list[datetime.date] = []
    for offset in range(chunk_size):
        day = cursor - datetime.timedelta(days=offset)
        if day < end_date:
            break
        days.append(day)
    return days


def _string_value(value: object, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _parse_date_value(value: object, default: datetime.date) -> datetime.date:
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and value:
        return datetime.date.fromisoformat(value)
    return default
