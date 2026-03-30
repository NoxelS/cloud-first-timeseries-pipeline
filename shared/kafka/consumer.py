"""Kafka consumer factories used by services."""

from __future__ import annotations

from kafka import KafkaConsumer

from shared.kafka.config import json_deserializer, kafka_bootstrap_servers


def create_json_consumer(
    topic: str,
    *,
    group_id: str,
    auto_offset_reset: str = "latest",
    enable_auto_commit: bool = False,
    **kwargs: object,
) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=kafka_bootstrap_servers(),
        auto_offset_reset=auto_offset_reset,
        enable_auto_commit=enable_auto_commit,
        group_id=group_id,
        value_deserializer=json_deserializer,
        **kwargs,
    )
