"""Feast feature views for grid frequency aggregations."""

from datetime import timedelta

from data_sources import grid_frequency_1h_source, grid_frequency_5m_source, grid_frequency_15m_source
from entities import series_id

from feast import FeatureView, Field
from feast.types import Float32, Int64

_feature_schema = [
    Field(name="frequency_mean_hz", dtype=Float32),
    Field(name="frequency_min_hz", dtype=Float32),
    Field(name="frequency_max_hz", dtype=Float32),
    Field(name="frequency_stddev_hz", dtype=Float32),
    Field(name="sample_count", dtype=Int64),
]

grid_frequency_5m_features = FeatureView(
    name="grid_frequency_5m_features",
    entities=[series_id],
    ttl=timedelta(days=30),
    schema=_feature_schema,
    source=grid_frequency_5m_source,
)

grid_frequency_15m_features = FeatureView(
    name="grid_frequency_15m_features",
    entities=[series_id],
    ttl=timedelta(days=30),
    schema=_feature_schema,
    source=grid_frequency_15m_source,
)

grid_frequency_1h_features = FeatureView(
    name="grid_frequency_1h_features",
    entities=[series_id],
    ttl=timedelta(days=90),
    schema=_feature_schema,
    source=grid_frequency_1h_source,
)
