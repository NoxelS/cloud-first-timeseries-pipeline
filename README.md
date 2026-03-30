# Cloud-First Time Series Pipeline

A modular, event-driven platform for time series data backed by Postgres, Kafka, Airflow, SQLAlchemy, and Atlas.

Architecture flow:
external sources → collector services → Kafka → Airflow pipelines → Postgres raw store → future ML workflows.

Database schema management lives in the shared SQLAlchemy ORM layer under `shared/db/`, and Atlas applies migrations through the `db-migrations` service before other database consumers start.

The design is service-oriented, containerized, and built to scale with independent components.
