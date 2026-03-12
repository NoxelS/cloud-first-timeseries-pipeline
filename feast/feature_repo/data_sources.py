"""Feast data source placeholders."""

from feast import FileSource

raw_event_source = FileSource(
    name="raw_event_source",
    path="data/raw_events.parquet",
    timestamp_field="event_timestamp",
)
