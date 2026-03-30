"""Kafka producer helpers shared by services and scripts."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from kafka import KafkaProducer
from kafka.errors import KafkaError

from shared.kafka.config import json_serializer, kafka_bootstrap_servers

logger = logging.getLogger(__name__)


@contextmanager
def producer_scope() -> Iterator[KafkaProducer]:
    """Create a short-lived producer for command-style publishes."""
    producer = KafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers(),
        value_serializer=json_serializer,
    )
    try:
        yield producer
    finally:
        producer.close()


def publish_event(topic: str, payload: dict[str, Any]) -> None:
    """Publish a JSON-serialized event to a Kafka topic."""
    if not payload:
        raise ValueError("payload must not be empty")  # noqa: TRY003

    with producer_scope() as producer:
        try:
            future = producer.send(topic, value=payload)
            record_metadata = future.get(timeout=10)
            logger.info(
                "Published event to %s (partition=%s, offset=%s)",
                record_metadata.topic,
                record_metadata.partition,
                record_metadata.offset,
            )
        except KafkaError:
            logger.exception("Failed to publish event to %s", topic)
            raise
