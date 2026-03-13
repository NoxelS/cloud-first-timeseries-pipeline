"""Energy-charts collector service.

Consumes collection commands from Kafka and publishes raw frequency events.
"""

from __future__ import annotations

import json
import logging
import os

from kafka import KafkaConsumer
from shared.kafka.topics import KafkaTopics
from collector import handle_collection_command


def _bootstrap_servers() -> str:
    return os.environ["KAFKA_BOOTSTRAP_SERVERS"]


def _topic_name() -> str:
    return KafkaTopics.CMD_FEATURE_COLLECTION.value


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
        group_id="feature-collection-consumer-group",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    try:
        for message in consumer:
            handle_collection_command(message.value)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
