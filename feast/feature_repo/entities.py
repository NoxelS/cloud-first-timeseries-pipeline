"""Feast entity placeholders."""

from feast import Entity

series_id = Entity(name="series_id", join_keys=["series_id"])
