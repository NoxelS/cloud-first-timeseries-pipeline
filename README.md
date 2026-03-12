# Cloud-First Time Series Pipeline

A modular, event-driven platform for time series data.

Architecture flow:
external sources → collector services → Kafka → Airflow pipelines → Feast feature store → future ML workflows.

The design is service-oriented, containerized, and built to scale with independent components.
