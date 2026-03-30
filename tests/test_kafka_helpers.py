from __future__ import annotations

import pytest

from shared.kafka.config import json_deserializer, json_serializer
from shared.kafka.producer import publish_event


def test_json_roundtrip() -> None:
    payload = {"hello": "world"}
    assert json_deserializer(json_serializer(payload)) == payload


def test_publish_event_rejects_empty_payload() -> None:
    with pytest.raises(ValueError):
        publish_event("raw.test.event", {})
