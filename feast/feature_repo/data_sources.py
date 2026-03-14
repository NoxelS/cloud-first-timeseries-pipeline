"""Feast data source definitions for frequency feature tables."""

# ruff: noqa: S608

import os

from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import PostgreSQLSource

_FEAST_SCHEMA = os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")

grid_frequency_5m_source = PostgreSQLSource(
    name="grid_frequency_5m_source",
    query=(
        "SELECT series_id, frequency_mean_hz, frequency_min_hz, frequency_max_hz, "
        "frequency_stddev_hz, sample_count, event_timestamp, created_at "
        f"FROM {_FEAST_SCHEMA}.grid_frequency_5m"
    ),
    timestamp_field="event_timestamp",
    created_timestamp_column="created_at",
)

grid_frequency_15m_source = PostgreSQLSource(
    name="grid_frequency_15m_source",
    query=(
        "SELECT series_id, frequency_mean_hz, frequency_min_hz, frequency_max_hz, "
        "frequency_stddev_hz, sample_count, event_timestamp, created_at "
        f"FROM {_FEAST_SCHEMA}.grid_frequency_15m"
    ),
    timestamp_field="event_timestamp",
    created_timestamp_column="created_at",
)

grid_frequency_1h_source = PostgreSQLSource(
    name="grid_frequency_1h_source",
    query=(
        "SELECT series_id, frequency_mean_hz, frequency_min_hz, frequency_max_hz, "
        "frequency_stddev_hz, sample_count, event_timestamp, created_at "
        f"FROM {_FEAST_SCHEMA}.grid_frequency_1h"
    ),
    timestamp_field="event_timestamp",
    created_timestamp_column="created_at",
)
