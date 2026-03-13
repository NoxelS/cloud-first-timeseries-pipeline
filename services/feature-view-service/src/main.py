from __future__ import annotations

# ruff: noqa: S608
import json
import logging
import os
from pathlib import Path
from typing import Any

import matplotlib
import pandas as pd
import psycopg
from kafka import KafkaConsumer
from ydata_profiling import ProfileReport

from shared.kafka.topics import KafkaTopics

matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def _kafka_bootstrap_servers() -> str:
    return os.environ["KAFKA_BOOTSTRAP_SERVERS"]


def _topic_name() -> str:
    return str(os.environ.get("KAFKA_TOPIC", KafkaTopics.FEATURES_ENERGY_CHARTS_UPDATED.value))


def _consumer_group() -> str:
    return os.environ.get("KAFKA_CONSUMER_GROUP", "feature-view-service")


def _output_dir() -> Path:
    return Path(os.environ.get("FEATURE_VIEW_OUTPUT_DIR", "/app/output"))


def _lookback_days() -> int:
    return int(os.environ.get("FEATURE_VIEW_LOOKBACK_DAYS", "30"))


def _max_rows() -> int:
    return int(os.environ.get("FEATURE_VIEW_MAX_ROWS", "20000"))


def _db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["FEAST_OFFLINE_STORE_HOST"],
        port=int(os.environ.get("FEAST_OFFLINE_STORE_PORT", "5432")),
        dbname=os.environ["FEAST_OFFLINE_STORE_DATABASE"],
        user=os.environ["FEAST_OFFLINE_STORE_USER"],
        password=os.environ["FEAST_OFFLINE_STORE_PASSWORD"],
    )


def _feature_schema() -> str:
    return os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")


def load_feature_frame() -> pd.DataFrame:
    schema = _feature_schema()
    query = f"""
        SELECT series_id, event_timestamp, frequency_hz, source_region, created_at
        FROM {schema}.grid_frequency_5m
        WHERE event_timestamp >= NOW() - (%s * interval '1 day')
        ORDER BY event_timestamp DESC
        LIMIT %s
    """

    with _db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(query, (_lookback_days(), _max_rows()))
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description or []]

    frame = pd.DataFrame(rows, columns=columns)
    if frame.empty:
        return frame

    frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True)
    frame["created_at"] = pd.to_datetime(frame["created_at"], utc=True)
    frame = frame.sort_values("event_timestamp")
    return frame


def _plot_timeseries(frame: pd.DataFrame, output_dir: Path) -> None:
    path = output_dir / "grid_frequency_timeseries.png"
    plt.figure(figsize=(14, 5))
    plt.plot(frame["event_timestamp"], frame["frequency_hz"], linewidth=1.0, color="#1f77b4")
    plt.title("Grid Frequency (5-Minute Aggregation)")
    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Frequency (Hz)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _plot_distribution(frame: pd.DataFrame, output_dir: Path) -> None:
    path = output_dir / "grid_frequency_distribution.png"
    plt.figure(figsize=(10, 5))
    frame["frequency_hz"].dropna().hist(bins=60, color="#ff7f0e", alpha=0.8)
    plt.title("Grid Frequency Distribution")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _write_profile(frame: pd.DataFrame, output_dir: Path) -> None:
    report_path = output_dir / "feature_profile_report.html"
    profile = ProfileReport(
        frame,
        title="Grid Frequency Feature Profile",
        minimal=True,
    )
    profile.to_file(report_path)


def _write_empty_notice(output_dir: Path) -> None:
    notice_path = output_dir / "README.txt"
    notice_path.write_text(
        "No rows available in feast.grid_frequency_5m for configured lookback window.\n",
        encoding="utf-8",
    )


def generate_artifacts(trigger_event: dict[str, Any]) -> None:
    out_dir = _output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    trigger_path = out_dir / "last_trigger_event.json"
    trigger_path.write_text(json.dumps(trigger_event, indent=2), encoding="utf-8")

    frame = load_feature_frame()
    if frame.empty:
        logger.warning("No feature rows available for reporting.")
        _write_empty_notice(out_dir)
        return

    _plot_timeseries(frame, out_dir)
    _plot_distribution(frame, out_dir)
    _write_profile(frame, out_dir)
    logger.info("Generated feature-view artifacts at %s", out_dir)


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    topic = _topic_name()

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=_kafka_bootstrap_servers(),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=_consumer_group(),
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )

    logger.info("Feature-view service listening on topic '%s'", topic)
    try:
        for message in consumer:
            payload = message.value if isinstance(message.value, dict) else {}
            logger.info(
                "Received trigger topic=%s partition=%s offset=%s",
                message.topic,
                message.partition,
                message.offset,
            )
            try:
                generate_artifacts(payload)
            except Exception:
                logger.exception("Failed to generate feature-view artifacts")
    finally:
        consumer.close()


if __name__ == "__main__":
    run()
