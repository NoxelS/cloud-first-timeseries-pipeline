"""Manual heartbeat trigger that stores a snapshot and publishes a Kafka event."""

from __future__ import annotations

import datetime
import logging
import uuid

from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    payload = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "source": "heartbeat_trigger",
        "payload": {"message": "heartbeat"},
    }
    publish_event(KafkaTopics.HEARTBEAT.value, payload)


if __name__ == "__main__":
    main()
