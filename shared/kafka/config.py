"""Shared Kafka configuration helpers."""

from __future__ import annotations

import json
from typing import Any

from shared.config import load_kafka_settings


def kafka_bootstrap_servers() -> str:
    return load_kafka_settings().bootstrap_servers


def json_serializer(value: dict[str, Any]) -> bytes:
    return json.dumps(value).encode("utf-8")


def json_deserializer(value: bytes) -> dict[str, Any]:
    return json.loads(value.decode("utf-8"))
