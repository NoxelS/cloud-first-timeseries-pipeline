from __future__ import annotations

# ruff: noqa: S608
import json
import logging
import os
import time
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

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
    return str(os.environ.get("KAFKA_TOPIC", KafkaTopics.RAW_ENERGY_CHARTS_UPDATED.value))


def _consumer_group() -> str | None:
    value = os.environ.get("KAFKA_CONSUMER_GROUP", "")
    if not value or value.lower() == "none":
        return None
    return value


def _output_dir() -> Path:
    return Path(os.environ.get("FEATURE_VIEW_OUTPUT_DIR", "/app/output"))


def _lookback_days() -> int:
    return int(os.environ.get("FEATURE_VIEW_LOOKBACK_DAYS", "30"))


def _max_rows() -> int:
    return int(os.environ.get("FEATURE_VIEW_MAX_ROWS", "20000"))


def _max_poll_interval_ms() -> int:
    return int(os.environ.get("KAFKA_MAX_POLL_INTERVAL_MS", "1800000"))


def _session_timeout_ms() -> int:
    return int(os.environ.get("KAFKA_SESSION_TIMEOUT_MS", "30000"))


def _profile_max_rows() -> int:
    return int(os.environ.get("FEATURE_VIEW_PROFILE_MAX_ROWS", "50000"))


def _display_timezone() -> ZoneInfo:
    return ZoneInfo(os.environ.get("FEATURE_VIEW_DISPLAY_TZ", "Europe/Berlin"))


def _db_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["FEAST_OFFLINE_STORE_HOST"],
        port=int(os.environ.get("FEAST_OFFLINE_STORE_PORT", "5432")),
        dbname=os.environ["FEAST_OFFLINE_STORE_DATABASE"],
        user=os.environ["FEAST_OFFLINE_STORE_USER"],
        password=os.environ["FEAST_OFFLINE_STORE_PASSWORD"],
    )


def _feast_schema() -> str:
    return os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")


def load_feature_frame(resolution: str) -> pd.DataFrame:
    schema = _feast_schema()
    table_name = {
        "5m": "grid_frequency_5m",
        "15m": "grid_frequency_15m",
        "1h": "grid_frequency_1h",
    }[resolution]
    query = f"""
        SELECT
            series_id,
            event_timestamp,
            frequency_mean_hz,
            frequency_min_hz,
            frequency_max_hz,
            frequency_stddev_hz,
            sample_count,
            created_at
        FROM {schema}.{table_name}
        ORDER BY event_timestamp ASC
    """

    rows: list[tuple[Any, ...]] = []
    with _db_connection() as conn, conn.cursor(name="feature_view_raw_cursor") as cursor:
        cursor.itersize = 100000
        cursor.execute(query)
        columns = [column.name for column in cursor.description or []]
        loaded = 0
        while True:
            chunk = cursor.fetchmany(100000)
            if not chunk:
                break
            rows.extend(chunk)
            loaded += len(chunk)
            if loaded % 500000 == 0:
                logger.info("Loaded %d rows for plotting", loaded)

    frame = pd.DataFrame(rows, columns=columns)
    if frame.empty:
        return frame

    frame["event_timestamp"] = pd.to_datetime(frame["event_timestamp"], utc=True)
    frame["created_at"] = pd.to_datetime(frame["created_at"], utc=True)
    frame = frame.sort_values("event_timestamp")
    frame["resolution"] = resolution
    return frame


def _plot_timeseries(frames: dict[str, pd.DataFrame], output_dir: Path) -> None:
    path = output_dir / "grid_frequency_timeseries.png"
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=False)
    for axis, resolution in zip(axes, ["5m", "15m", "1h"], strict=True):
        frame = frames[resolution]
        local_ts = frame["event_timestamp"].dt.tz_convert(_display_timezone())
        axis.plot(local_ts, frame["frequency_mean_hz"], linewidth=1.0, color="#1f77b4")
        axis.set_title(f"Grid Frequency Mean ({resolution})")
        axis.set_xlabel(f"Timestamp ({_display_timezone().key})")
        axis.set_ylabel("Frequency (Hz)")
        axis.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_distribution(frame: pd.DataFrame, output_dir: Path) -> None:
    path = output_dir / "grid_frequency_distribution.png"
    plt.figure(figsize=(10, 5))
    frame["frequency_mean_hz"].dropna().hist(bins=60, color="#ff7f0e", alpha=0.8)
    plt.title("Grid Frequency Distribution")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _plot_intraday(frames: dict[str, pd.DataFrame], output_dir: Path) -> None:
    path = output_dir / "grid_frequency_intraday.png"
    tz = _display_timezone()
    local_today = pd.Timestamp.now(tz=tz).date()

    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=False)
    for axis, resolution in zip(axes, ["5m", "15m", "1h"], strict=True):
        frame = frames[resolution]
        local_ts = frame["event_timestamp"].dt.tz_convert(tz)
        intraday_mask = local_ts.dt.date == local_today
        intraday_frame = frame.loc[intraday_mask].copy()
        if intraday_frame.empty:
            axis.text(0.5, 0.5, "No data for local day", ha="center", va="center", transform=axis.transAxes)
            axis.set_title(f"Intraday Grid Frequency ({resolution})")
            axis.set_xlabel(f"Time ({tz.key})")
            axis.set_ylabel("Frequency (Hz)")
            axis.grid(alpha=0.3)
            continue

        intraday_local_ts = intraday_frame["event_timestamp"].dt.tz_convert(tz)
        axis.plot(intraday_local_ts, intraday_frame["frequency_mean_hz"], linewidth=1.2, color="#2a9d8f")
        axis.set_title(f"Intraday Grid Frequency ({resolution}) - {local_today.isoformat()}")
        axis.set_xlabel(f"Time ({tz.key})")
        axis.set_ylabel("Frequency (Hz)")
        axis.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _write_profile(frame: pd.DataFrame, output_dir: Path) -> None:
    profile_frame = frame.copy()
    profile_frame["event_timestamp_local"] = profile_frame["event_timestamp"].dt.tz_convert(_display_timezone())
    profile_frame["created_at_local"] = profile_frame["created_at"].dt.tz_convert(_display_timezone())
    max_rows = _profile_max_rows()
    if len(profile_frame) > max_rows:
        profile_frame = profile_frame.tail(max_rows)
        logger.info("Profiling sampled frame with %d/%d rows", len(profile_frame), len(frame))

    report_path = output_dir / "feature_profile_report.html"
    profile = ProfileReport(
        profile_frame,
        title="Grid Frequency Feature Profile",
        minimal=True,
        progress_bar=False,
    )
    profile.to_file(report_path)


def _write_empty_notice(output_dir: Path) -> None:
    notice_path = output_dir / "README.txt"
    notice_path.write_text(
        "No rows available in feast.grid_frequency_[5m|15m|1h] for plotting.\n",
        encoding="utf-8",
    )


def generate_artifacts(trigger_event: dict[str, Any]) -> None:
    out_dir = _output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    trigger_path = out_dir / "last_trigger_event.json"
    trigger_path.write_text(json.dumps(trigger_event, indent=2), encoding="utf-8")

    logger.info("Loading Feast feature frames from database")
    frames = {
        "5m": load_feature_frame("5m"),
        "15m": load_feature_frame("15m"),
        "1h": load_feature_frame("1h"),
    }
    if any(frame.empty for frame in frames.values()):
        logger.warning("One or more Feast feature tables are empty; skipping artifacts.")
        _write_empty_notice(out_dir)
        return

    profile_frame = pd.concat([frames["5m"], frames["15m"], frames["1h"]], ignore_index=True)
    logger.info(
        "Generating plots from rows: 5m=%d 15m=%d 1h=%d",
        len(frames["5m"]),
        len(frames["15m"]),
        len(frames["1h"]),
    )
    _plot_timeseries(frames, out_dir)
    _plot_intraday(frames, out_dir)
    _plot_distribution(frames["5m"], out_dir)
    logger.info("Generating profiling report")
    _write_profile(profile_frame, out_dir)
    logger.info("Generated feature-view artifacts at %s", out_dir)


def run() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    while True:
        topic = _topic_name()
        group_id = _consumer_group()
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=_kafka_bootstrap_servers(),
            auto_offset_reset="latest",
            enable_auto_commit=bool(group_id),
            group_id=group_id,
            max_poll_records=1,
            max_poll_interval_ms=_max_poll_interval_ms(),
            session_timeout_ms=_session_timeout_ms(),
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )

        logger.info("Feature-view service listening on topic '%s'", topic)
        try:
            while True:
                messages = consumer.poll(timeout_ms=1000, max_records=1)
                if not messages:
                    continue

                for _, records in messages.items():
                    for message in records:
                        payload = message.value if isinstance(message.value, dict) else {}
                        logger.info(
                            "Received trigger topic=%s partition=%s offset=%s",
                            message.topic,
                            message.partition,
                            message.offset,
                        )
                        try:
                            generate_artifacts(payload)
                            if group_id:
                                consumer.commit()
                        except BaseException:
                            logger.exception("Failed to generate feature-view artifacts")
        except BaseException:
            logger.exception("Feature-view consumer loop crashed, retrying in 5 seconds")
            time.sleep(5)
        finally:
            consumer.close()


if __name__ == "__main__":
    run()
