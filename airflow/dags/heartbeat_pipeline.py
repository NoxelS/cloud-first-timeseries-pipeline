"""Heartbeat pipeline DAG - captures Kafka offsets and system checks."""

from __future__ import annotations

import datetime
from airflow.decorators import dag, task

from shared.config import heartbeat_cron
from shared.heartbeat import plot_offsets, resolve_output_path, run_heartbeat


@dag(
    dag_id="heartbeat_pipeline",
    description="Collects system heartbeat checks and stores them in Postgres.",
    schedule=heartbeat_cron(),
    start_date=datetime.datetime(2026, 3, 12, tzinfo=datetime.timezone.utc),
    catchup=False,
    tags=["heartbeat"],
)
def heartbeat_pipeline() -> None:
    @task()
    def record_heartbeat() -> None:
        run_heartbeat()
        plot_offsets(resolve_output_path())

    record_heartbeat()


heartbeat_pipeline()
