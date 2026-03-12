"""Test event consumer service.

Consumes events from Kafka and prints each event payload to stdout.
"""

from __future__ import annotations

import json
import logging
import os

from kafka import KafkaConsumer


def _bootstrap_servers() -> str:
    return os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka-broker:29092")


def _topic_name() -> str:
    return os.environ.get("KAFKA_TOPIC", "raw.test.event")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    bootstrap = _bootstrap_servers()
    topic = _topic_name()

    logging.info("Starting test consumer on topic '%s' via %s", topic, bootstrap)

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="test-consumer-group",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    try:
        for message in consumer:
            print(f"[test-consumer] topic={message.topic} partition={message.partition} offset={message.offset}")
            print(json.dumps(message.value, ensure_ascii=False))
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
