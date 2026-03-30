from __future__ import annotations

import logging
import sys
from collections.abc import Iterable

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from shared.config import load_kafka_settings
from shared.kafka.topics import KafkaTopics


def _collect_topic_names() -> Iterable[str]:
    """Collect topic names declared in the shared Kafka enum."""

    return [topic.value for topic in KafkaTopics]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    topic_names = list(_collect_topic_names())
    if not topic_names:
        logging.error("No Kafka topic names found in shared.kafka.topics")
        sys.exit(1)

    settings = load_kafka_settings()
    bootstrap = settings.bootstrap_servers
    logging.info("Connecting to Kafka bootstrap servers: %s", bootstrap)

    admin = KafkaAdminClient(bootstrap_servers=bootstrap)

    new_topics = [
        NewTopic(
            name=name,
            num_partitions=settings.default_partitions,
            replication_factor=settings.default_replication_factor,
        )
        for name in topic_names
    ]

    try:
        admin.create_topics(new_topics=new_topics, validate_only=False)
        logging.info("Requested creation of %d topics", len(new_topics))
    except TopicAlreadyExistsError as exc:  # pragma: no cover - defensive
        logging.warning("Some topics already exist: %s", exc)
    except Exception:  # pragma: no cover - surface error
        logging.exception("Failed to create topics")
        sys.exit(3)
    finally:
        try:
            admin.close()
            logging.info("See message above for any warnings or errors during topic creation.")
        except Exception:  # pragma: no cover - surface error
            logging.exception("Failed to close Kafka admin client")


if __name__ == "__main__":
    main()
