# Cloud-First Time Series Pipeline

A modular, event-driven platform for time series data backed by Postgres, Kafka, Airflow, SQLAlchemy, and Atlas.

Architecture flow:
external sources → collector services → Kafka → Airflow pipelines → Postgres raw store → future ML workflows.

The `energy-charts-backfill-service` consumes `cmd.energy_charts.backfill` and fills `raw.energy_charts_frequency` day-by-day backward to `2023-01-01`.

Database schema management lives in the shared SQLAlchemy ORM layer under `shared/db/`, and Atlas applies migrations through the `db-migrations` service before other database consumers start.

## Manual backfill trigger

Use the helper script to publish a backfill command event to Kafka:

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 uv run python scripts/trigger_energy_charts_backfill.py --start-date 2026-03-13 --end-date 2023-01-01 --region DE-Freiburg
```

If `--start-date` is omitted, the script uses today (UTC). If `--end-date` is omitted, it defaults to `2023-01-01`.

The design is service-oriented, containerized, and built to scale with independent components.
