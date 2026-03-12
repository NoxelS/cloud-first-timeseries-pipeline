"""Feast entity placeholders."""

from feast import Entity, ValueType

series_id = Entity(name="series_id", join_keys=["series_id"], value_type=ValueType.STRING)
