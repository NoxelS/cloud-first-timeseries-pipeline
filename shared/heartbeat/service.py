"""Heartbeat collection and persistence."""

from __future__ import annotations

import datetime
import logging
import socket
import time
from typing import Any

from kafka import KafkaConsumer
from kafka.structs import TopicPartition
from sqlalchemy import text

from shared.config import load_database_settings, load_heartbeat_settings
from shared.db.models.heartbeat import HeartbeatEvent
from shared.db.session import session_scope
from shared.kafka.config import kafka_bootstrap_servers

logger = logging.getLogger(__name__)


def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc)


def _parse_bootstrap_servers(bootstrap: str) -> list[tuple[str, int]]:
    servers: list[tuple[str, int]] = []
    for entry in bootstrap.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" in entry:
            host, port_str = entry.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                continue
        else:
            host = entry
            port = 9092
        if host:
            servers.append((host, port))
    return servers


def _check_tcp(host: str, port: int, *, timeout_seconds: float = 2.0) -> dict[str, Any]:
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            latency_ms = int((time.monotonic() - start) * 1000)
            return {"ok": True, "latency_ms": latency_ms}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def _collect_tcp_checks() -> dict[str, Any]:
    database_settings = load_database_settings()
    checks: dict[str, Any] = {
        "database": {
            "target": f"{database_settings.host}:{database_settings.port}",
            **_check_tcp(database_settings.host, database_settings.port),
        },
        "kafka": {},
    }

    for host, port in _parse_bootstrap_servers(kafka_bootstrap_servers()):
        checks["kafka"][f"{host}:{port}"] = _check_tcp(host, port)

    return checks


def collect_kafka_snapshot(*, include_internal_topics: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    consumer: KafkaConsumer | None = None
    bootstrap = kafka_bootstrap_servers()

    try:
        consumer = KafkaConsumer(bootstrap_servers=bootstrap, enable_auto_commit=False)
        topics = consumer.topics()
        if not include_internal_topics:
            topics = {topic for topic in topics if not topic.startswith("__")}

        offsets: dict[str, Any] = {}
        partition_count = 0

        for topic in sorted(topics):
            partitions = consumer.partitions_for_topic(topic) or set()
            partition_count += len(partitions)
            topic_partitions = [TopicPartition(topic, partition) for partition in sorted(partitions)]
            if not topic_partitions:
                offsets[topic] = {}
                continue

            beginning = consumer.beginning_offsets(topic_partitions)
            end = consumer.end_offsets(topic_partitions)
            offsets[topic] = {
                str(tp.partition): {"beginning": beginning.get(tp), "end": end.get(tp)}
                for tp in topic_partitions
            }

        stats = {
            "ok": True,
            "bootstrap_servers": bootstrap,
            "topic_count": len(topics),
            "partition_count": partition_count,
            "bootstrap_connected": consumer.bootstrap_connected(),
        }
        return offsets, stats
    except Exception as exc:
        logger.exception("Failed to collect Kafka offsets")
        return {}, {"ok": False, "error": str(exc), "bootstrap_servers": bootstrap}
    finally:
        if consumer is not None:
            consumer.close()


def _check_database() -> dict[str, Any]:
    settings = load_database_settings()
    status: dict[str, Any] = {
        "ok": True,
        "host": settings.host,
        "port": settings.port,
        "database": settings.database,
        "schema": settings.schema,
    }

    try:
        with session_scope() as session:
            session.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception("Database heartbeat check failed")
        status["ok"] = False
        status["error"] = str(exc)

    return status


def run_heartbeat() -> HeartbeatEvent:
    heartbeat_at = _utc_now()
    settings = load_heartbeat_settings()

    kafka_offsets, kafka_status = collect_kafka_snapshot(
        include_internal_topics=settings.include_internal_topics,
    )
    database_status = _check_database()

    system_checks = {
        "checked_at": heartbeat_at.isoformat(),
        "kafka": kafka_status,
        "database": database_status,
        "tcp": _collect_tcp_checks(),
    }

    event = HeartbeatEvent(
        heartbeat_at=heartbeat_at,
        kafka_offsets=kafka_offsets,
        system_checks=system_checks,
    )

    with session_scope() as session:
        session.add(event)

    logger.info("Heartbeat stored", extra={"heartbeat_id": str(event.id)})
    return event
