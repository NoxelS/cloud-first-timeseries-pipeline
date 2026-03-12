"""Test DAG – publishes a heartbeat event to the raw.test.event topic every minute."""

from __future__ import annotations

import datetime
import uuid

from airflow.decorators import dag, task


@dag(
    dag_id="test_pipeline",
    description="Publishes a heartbeat event to KafkaTopics.TEST every minute.",
    schedule="* * * * *",
    start_date=datetime.datetime(2026, 3, 12),
    catchup=False,
    tags=["test"],
)
def test_pipeline() -> None:
    @task()
    def send_test_event() -> None:
        import json
        import os

        from kafka import KafkaProducer

        bootstrap = os.environ["KAFKA_BOOTSTRAP_SERVERS"]

        producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "source": "test_pipeline",
            "payload": {"message": "heartbeat"},
        }
        producer.send("raw.test.event", value=event)
        producer.flush()
        producer.close()

    send_test_event()


test_pipeline()
