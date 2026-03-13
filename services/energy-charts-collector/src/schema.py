from __future__ import annotations

def make_series_id(country: str, production_type: str) -> str:
    """Return a canonical series id for a given country and production type."""
    return f"{country}::{production_type}"
