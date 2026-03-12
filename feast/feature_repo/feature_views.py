"""Feast feature view placeholders."""

from datetime import timedelta

from feast import FeatureView, Field
from feast.types import Float32

from data_sources import raw_event_source
from entities import series_id

series_features = FeatureView(
    name="series_features",
    entities=[series_id],
    ttl=timedelta(days=1),
    schema=[Field(name="value", dtype=Float32)],
    source=raw_event_source,
)
