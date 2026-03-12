"""Kafka producer utility."""

from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger(__name__)


def publish_event(topic: str, payload: dict) -> None:
    """Publish a JSON-serialised event to a Kafka topic.
    """
    from kafka import KafkaProducer
    from kafka.errors import KafkaError

    bootstrap = os.environ["KAFKA_BOOTSTRAP_SERVERS"]

    producer = KafkaProducer(
        bootstrap_servers=bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    try:
        future = producer.send(topic, value=payload)
        record_metadata = future.get(timeout=10)
        logger.info(
            "Published event to %s (partition=%s, offset=%s)",
            record_metadata.topic,
            record_metadata.partition,
            record_metadata.offset,
        )
    except KafkaError as exc:
        logger.exception("Failed to publish event to %s: %s", topic, exc)
        raise
    finally:
        producer.close()
