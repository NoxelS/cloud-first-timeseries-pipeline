"""Heartbeat event consumer service.

Consumes events from Kafka and prints each event payload to stdout.
"""

from __future__ import annotations

import json
import logging
import os

from shared.heartbeat.plot_offsets import plot_offsets, resolve_output_path
from shared.heartbeat.service import run_heartbeat
from shared.kafka.consumer import create_json_consumer
from shared.kafka.topics import KafkaTopics


def _topic_name() -> str:
    topic = os.environ.get("KAFKA_TOPIC", KafkaTopics.HEARTBEAT.value)
    return topic or KafkaTopics.HEARTBEAT.value



def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    topic = _topic_name()

    logging.info("Starting heartbeat consumer on topic '%s'", topic)

    consumer = create_json_consumer(topic, group_id="heartbeat-consumer-group")

    try:
        for message in consumer:
            print(f"[heartbeat-consumer] topic={message.topic} partition={message.partition} offset={message.offset}")
            print(json.dumps(message.value, ensure_ascii=False))
            run_heartbeat()
            plot_offsets(resolve_output_path())
            consumer.commit()
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
