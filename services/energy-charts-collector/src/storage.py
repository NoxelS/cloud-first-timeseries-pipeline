"""Legacy storage helpers (unused by collector, kept for reference).

Collector now publishes raw events to Kafka and Airflow persists them.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import psycopg
from psycopg import sql


def _connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["FEAST_OFFLINE_STORE_HOST"],
        port=int(os.environ.get("FEAST_OFFLINE_STORE_PORT", "5432")),
        dbname=os.environ["FEAST_OFFLINE_STORE_DATABASE"],
        user=os.environ["FEAST_OFFLINE_STORE_USER"],
        password=os.environ["FEAST_OFFLINE_STORE_PASSWORD"],
    )


def _schema_name() -> str:
    return os.environ.get("FEAST_OFFLINE_STORE_SCHEMA", "feast")


def ensure_frequency_table(conn: psycopg.Connection) -> None:
    schema = _schema_name()
    with conn.cursor() as cursor:
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
        cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.grid_frequency_5m (
                    series_id TEXT NOT NULL,
                    event_timestamp TIMESTAMPTZ NOT NULL,
                    frequency_hz DOUBLE PRECISION NULL,
                    source_region TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (series_id, event_timestamp)
                )
                """
            ).format(sql.Identifier(schema))
        )
        cursor.execute(
            sql.SQL(
                """
                CREATE INDEX IF NOT EXISTS ix_grid_frequency_5m_event_timestamp
                ON {}.grid_frequency_5m (event_timestamp)
                """
            ).format(sql.Identifier(schema))
        )


def insert_frequency_rows(rows: List[Dict[str, Any]]) -> int:
    if not rows:
        return 0

    unique_rows: List[Dict[str, Any]] = []
    seen_keys: set[tuple[str, Any]] = set()
    for row in rows:
        key = (row["series_id"], row["event_timestamp"])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_rows.append(row)

    schema = _schema_name()
    inserted_count = 0
    with _connection() as conn:
        ensure_frequency_table(conn)
        with conn.cursor() as cursor:
            for row in unique_rows:
                cursor.execute(
                    sql.SQL(
                        """
                        INSERT INTO {}.grid_frequency_5m (series_id, event_timestamp, frequency_hz, source_region)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (series_id, event_timestamp)
                        DO UPDATE SET
                            frequency_hz = EXCLUDED.frequency_hz,
                            source_region = EXCLUDED.source_region,
                            created_at = NOW()
                        RETURNING 1
                        """
                    ).format(sql.Identifier(schema)),
                    (
                        row["series_id"],
                        row["event_timestamp"],
                        row["frequency_hz"],
                        row["source_region"],
                    ),
                )
                if cursor.fetchone() is not None:
                    inserted_count += 1
        conn.commit()

    return inserted_count
