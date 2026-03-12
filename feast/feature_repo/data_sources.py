"""Feast data source placeholders."""

from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import PostgreSQLSource

raw_event_source = PostgreSQLSource(
    name="raw_event_source",
    query="SELECT series_id, value, event_timestamp FROM raw_events",
    timestamp_field="event_timestamp",
)
