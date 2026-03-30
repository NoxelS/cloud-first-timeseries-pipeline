"""Plot Kafka topic offsets from heartbeat history."""

from __future__ import annotations

import argparse
import datetime
import logging
import os
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from sqlalchemy import select

from shared.db.models.heartbeat import HeartbeatEvent
from shared.db.session import session_scope

logger = logging.getLogger(__name__)


def default_output_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "artifacts" / "heartbeat" / "latest_heartbeat.png"


def resolve_output_path() -> Path:
    return Path(os.environ.get("HEARTBEAT_PLOT_OUTPUT", str(default_output_path())))


def _normalize_timestamp(value: datetime.datetime) -> datetime.datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(datetime.timezone.utc).replace(tzinfo=None)


def _sum_partition_ends(offsets: dict[str, Any]) -> int | None:
    total = 0
    has_value = False
    for partition_info in offsets.values():
        if not isinstance(partition_info, dict):
            continue
        end_offset = partition_info.get("end")
        if end_offset is None:
            continue
        total += int(end_offset)
        has_value = True
    return total if has_value else None


def _fetch_heartbeat_offsets() -> list[tuple[datetime.datetime, dict[str, Any]]]:
    with session_scope() as session:
        rows = session.execute(
            select(HeartbeatEvent.heartbeat_at, HeartbeatEvent.kafka_offsets).order_by(HeartbeatEvent.heartbeat_at)
        ).all()
    return [(row[0], row[1] or {}) for row in rows]


def _build_series(
    rows: list[tuple[datetime.datetime, dict[str, Any]]],
) -> tuple[list[datetime.datetime], dict[str, list[int | None]]]:
    timestamps: list[datetime.datetime] = []
    topic_series: dict[str, list[int | None]] = {}

    for heartbeat_at, kafka_offsets in rows:
        timestamps.append(_normalize_timestamp(heartbeat_at))
        for series in topic_series.values():
            series.append(None)

        for topic, partitions in kafka_offsets.items():
            if not isinstance(partitions, dict):
                continue
            if topic not in topic_series:
                topic_series[topic] = [None] * len(timestamps)
            topic_series[topic][-1] = _sum_partition_ends(partitions)

    return timestamps, topic_series


def plot_offsets(output_path: Path) -> None:
    rows = _fetch_heartbeat_offsets()
    if not rows:
        logger.warning("No heartbeat events found; no plot generated.")
        return

    timestamps, topic_series = _build_series(rows)
    if not topic_series:
        logger.warning("No Kafka offsets available in heartbeat events; no plot generated.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    for topic, values in sorted(topic_series.items()):
        ax.plot(timestamps, values, label=topic)

    ax.set_title("Kafka topic end offsets from heartbeat history")
    ax.set_xlabel("Heartbeat time (UTC)")
    ax.set_ylabel("End offset sum")
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M"))
    fig.autofmt_xdate()
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

    logger.info("Saved heartbeat plot to %s", output_path)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot Kafka offsets from heartbeat events.")
    parser.add_argument("--output", default=str(resolve_output_path()), help="Output image path")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _parse_args()
    plot_offsets(Path(args.output))


if __name__ == "__main__":
    main()
