"""Test DAG - publishes a heartbeat event to the raw.test.event topic every minute."""

from __future__ import annotations

import datetime
import uuid

from airflow.decorators import dag, task

from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics


@dag(
    dag_id="test_pipeline",
    description="Publishes a heartbeat event to KafkaTopics.TEST every minute.",
    schedule="* * * * *",
    start_date=datetime.datetime(2026, 3, 12, tzinfo=datetime.timezone.utc),
    catchup=False,
    tags=["test"],
)
def test_pipeline() -> None:
    @task()
    def send_test_event() -> None:
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            "source": "test_pipeline",
            "payload": {"message": "heartbeat"},
        }
        publish_event(KafkaTopics.TEST.value, event)

    send_test_event()


test_pipeline()
