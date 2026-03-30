"""Series naming helpers."""

from __future__ import annotations


def series_id_for_region(region: str) -> str:
    return f"{region.lower()}::grid_frequency"
