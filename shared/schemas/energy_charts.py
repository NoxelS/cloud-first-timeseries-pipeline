"""Typed command and event payloads for Energy Charts flows."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BackfillCommandPayload:
    event_id: str
    timestamp: str
    request_id: str
    region: str
    start_date: str
    end_date: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class RawUpdatePayload:
    event_id: str
    timestamp: str
    source: str
    pipeline: str
    series_id: str
    window_start: str
    window_end: str
    rows_written: int

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)
