"""DAG that emits a feature-collection command to Kafka every 5 minutes.

The DAG only publishes a command to `CMD_FEATURE_COLLECTION` and does not
perform collection itself.
"""

from __future__ import annotations

import datetime
import uuid

from airflow.decorators import dag, task
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics


@dag(
    dag_id="feature_collection_request",
    description="Emit a collection command to collectors every 5 minutes.",
    schedule="*/5 * * * *",
    start_date=datetime.datetime(2026, 3, 13),
    catchup=False,
    tags=["energy-charts"],
)
def feature_collection_request() -> None:
    @task()
    def send_collection_command() -> None:
        event = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "source": "feature_collection_request",
            "datasets": "all",
            "scope": "all",
        }
        publish_event(KafkaTopics.CMD_FEATURE_COLLECTION.value, event)

    send_collection_command()


feature_collection_request()
