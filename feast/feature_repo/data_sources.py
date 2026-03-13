"""Feast data source placeholders."""

import os

from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import PostgreSQLSource

_FEAST_SCHEMA = os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")

raw_event_source = PostgreSQLSource(
    name="grid_frequency_5m_source",
    query=(
        "SELECT series_id, frequency_hz, event_timestamp, created_at "
        f"FROM {_FEAST_SCHEMA}.grid_frequency_5m"
    ),
    timestamp_field="event_timestamp",
    created_timestamp_column="created_at",
)
