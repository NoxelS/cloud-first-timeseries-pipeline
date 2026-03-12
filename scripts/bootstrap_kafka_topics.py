

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Iterable

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from shared.kafka.topics import KafkaTopics

KAFKA_DEFAULT_PARTITIONS = 3
KAFKA_DEFAULT_REPLICATION = 1


def _get_bootstrap_servers() -> str:
    return os.environ["KAFKA_BOOTSTRAP_SERVERS"]


def _collect_topic_names() -> Iterable[str]:
    """Collect topic name constants from shared.kafka.topics.

    Any module-level UPPER_CASE string value is considered a topic name.
    """

    return [topic.value for topic in KafkaTopics]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    topic_names = list(_collect_topic_names())
    if not topic_names:
        logging.error("No Kafka topic names found in shared.kafka.topics")
        sys.exit(1)

    bootstrap = _get_bootstrap_servers()
    logging.info("Connecting to Kafka bootstrap servers: %s", bootstrap)

    admin = KafkaAdminClient(bootstrap_servers=bootstrap)

    # Topic creation defaults; make these configurable via env if needed.
    num_partitions = int(os.environ.get("KAFKA_DEFAULT_PARTITIONS", str(KAFKA_DEFAULT_PARTITIONS)))
    replication_factor = int(os.environ.get("KAFKA_DEFAULT_REPLICATION", str(KAFKA_DEFAULT_REPLICATION)))

    new_topics = [
        NewTopic(name=n, num_partitions=num_partitions, replication_factor=replication_factor) for n in topic_names
    ]

    try:
        admin.create_topics(new_topics=new_topics, validate_only=False)
        logging.info(f"Requested creation of {len(new_topics)} topics")
    except TopicAlreadyExistsError as e:  # pragma: no cover - defensive
        logging.warning(f"Some topics already exist: {e}")
    except Exception as exc:  # pragma: no cover - surface error
        logging.exception(f"Failed to create topics: {exc}")
        sys.exit(3)
    finally:
        try:
            admin.close()
            logging.info("See message above for any warnings or errors during topic creation.")
        except Exception as exc:  # pragma: no cover - surface error
            logging.exception(f"Failed to close Kafka admin client: {exc}")


if __name__ == "__main__":
    main()
