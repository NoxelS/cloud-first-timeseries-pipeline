"""Heartbeat pipeline DAG - captures Kafka offsets and system checks."""

from __future__ import annotations

import datetime
import uuid
from airflow.decorators import dag, task

from shared.config import heartbeat_cron
from shared.kafka.producer import publish_event
from shared.kafka.topics import KafkaTopics


@dag(
    dag_id="heartbeat_pipeline",
    description="Publishes a heartbeat event to Kafka.",
    schedule=heartbeat_cron(),
    start_date=datetime.datetime(2026, 3, 12, tzinfo=datetime.timezone.utc),
    catchup=False,
    tags=["heartbeat"],
)
def heartbeat_pipeline() -> None:
    @task()
    def publish_heartbeat_event() -> None:
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
            "source": "heartbeat_pipeline",
            "payload": {"message": "heartbeat"},
        }
        publish_event(KafkaTopics.HEARTBEAT.value, event)

    publish_heartbeat_event()


heartbeat_pipeline()
