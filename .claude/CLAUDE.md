# CLAUDE.md

## Purpose

This repository implements a **modular data platform for collecting external data, generating features, and preparing data for machine learning pipelines**.

The system follows an **event-driven microservice architecture** built around:

- Kafka for event streaming
- Airflow for pipeline orchestration
- PostgreSQL for raw time-series storage
- Docker for local infrastructure
- Python for services

The platform is designed to evolve over time. Agents and developers should **extend the system without restructuring the repository**.

This document describes:

- the architectural philosophy
- repository structure
- development conventions
- service responsibilities
- testing and reliability guidelines

Agents modifying the repository must follow these principles.

---

# High-Level Architecture

The system processes data through several stages.

External Data Sources
↓
Data Collector Services
↓
Kafka Topics
↓
Airflow Pipelines
↓
PostgreSQL Raw Store
↓
Future Training Pipelines

Core idea:

- **Collectors gather data**
- **Kafka transports events**
- **Airflow orchestrates processing**
- **PostgreSQL stores raw time-series data**

---

# Design Principles

## 1. Event-driven architecture

All data ingestion flows through Kafka.

Services should **publish events instead of directly calling other services**.

Correct pattern:
service → Kafka topic → consumer

Avoid:
service → direct API call → service

Event streaming makes the system scalable and loosely coupled.

---

## 2. Stateless services

All containers **must be stateless**.

This means:

- services do not store data locally
- services can be restarted without losing state
- services can run multiple replicas

Persistent data must be stored in:

- Kafka
- databases
- object storage
- feature stores

Never store important data in container filesystems.

---

## 3. Single responsibility services

Each service should have **one clear responsibility**.

Examples:
eurostat_collector → collect EUROSTAT data
weather_collector → collect weather data
feature_pipeline → compute features

Avoid creating services that do multiple unrelated tasks.

---

## 4. Clear data pipeline stages

The platform follows a standard data lifecycle.

ingestion → transport → transformation → persistence

Responsibilities:

| Stage | Tool |
|-----|------|
| ingestion | collectors |
| transport | Kafka |
| orchestration | Airflow |
| persistence | PostgreSQL |

Services should respect these boundaries.

---

## 5. Reproducible environments

All services must run inside containers.

Dependencies are managed with **uv**.

Each service should define its own dependencies.

---

## 6. Code should be testable

Code must be structured so it can be tested.

Avoid putting logic directly in:

- Airflow DAG files
- service entrypoints
- scripts

Instead move logic into reusable modules.

---

# Repository Structure

The repository is organized into several logical layers.

infra/
services/
airflow/
shared/
tests/
scripts/

Each layer has a specific role.

---

# Infrastructure
infra/

Contains Docker infrastructure and local development environment.

Examples:
docker-compose
Kafka configuration
Airflow configuration
database setup

Infrastructure code should **not contain business logic**.

---

# Services
services/

Contains microservices responsible for **data collection from external sources**.

Example structure:
services/
    source_collector/
        src/
        tests/
        Dockerfile
        pyproject.toml

Each collector service:

1. fetches data from an external source
2. normalizes the data
3. publishes events to Kafka

Collectors should **not perform heavy transformations**.

---

# Airflow
airflow/

Contains DAGs used for pipeline orchestration.

Airflow responsibilities:

- scheduling
- task orchestration
- running data pipelines

DAGs should remain **thin orchestration layers**.

Avoid placing complex data processing logic inside DAG files.

Instead import reusable modules from services or shared libraries.

---

# Shared Code
shared/

Contains reusable utilities used by multiple services.

Examples:
Kafka utilities
event schemas
configuration helpers

Shared code must remain **small and stable**.

Avoid turning the shared module into a monolithic library.

---

# Tests
tests/

Tests ensure reliability of the platform.

Three levels of tests should exist.

### Unit tests

Located near the code they test.

Example:
services/source_collector/tests

These test individual functions or modules.

---

### Integration tests

Located in:
tests/integration

Integration tests verify interactions between components such as:

- Kafka pipelines
- feature pipelines
- service communication

---

### End-to-end tests

These validate the full data pipeline:
collector → Kafka → pipeline → feature store

---

# Scripts
scripts/

Contains developer utilities such as:

- initializing Kafka topics
- triggering manual jobs
- debugging pipelines

Scripts should not contain production logic.

---

# Service Development Guidelines

When creating a new service:

1. create a new directory inside `services/`
2. implement the service logic
3. publish events to Kafka
4. add unit tests
5. create a Dockerfile

Example service structure:
services/new_collector/
    src/
        main.py
        client.py
        producer.py

    tests/
    Dockerfile
    pyproject.toml

---

# Event Design

Events are the primary communication mechanism.

Events should be:

- immutable
- small
- self-describing

Typical event structure:
key
timestamp
payload
metadata

Large datasets should not be sent through Kafka.

Instead store large data externally and send references.

---

# Adding New Data Sources

To add a new source:

1. create a new collector service
2. define a Kafka topic
3. publish raw events
4. update feature pipelines if needed

Avoid modifying existing collectors when adding new sources.

---

# Container Guidelines

Containers should follow these rules:

- stateless
- reproducible
- small images
- minimal runtime dependencies

Containers must not store persistent state.

Persistent state must live in external systems.

---

# Error Handling

Services should fail loudly and early.

Recommended practices:

- validate input data
- log structured errors
- retry transient failures
- avoid silent failures

---

# Logging

All services should produce structured logs.

Logs should include:
timestamp
service name
event id
error messages

Logs are critical for debugging distributed systems.

---

# Observability

The system should eventually support monitoring for:

- pipeline failures
- Kafka consumer lag
- feature freshness
- system metrics

Monitoring infrastructure may be added later.

---

# Evolution of the Platform

The architecture is intentionally simple.

Future components may include:

- experiment tracking
- distributed training
- data validation
- feature monitoring
- model serving

These should integrate without major structural changes.

---

# Agent Responsibilities

Agents modifying the repository must:

- follow architectural principles
- maintain test coverage
- keep services isolated
- avoid tightly coupled designs
- document new modules

Agents should prefer **small incremental improvements** over large refactors.

---

# Key Philosophy

The repository should remain:

- modular
- observable
- testable
- scalable

Prefer simple designs that can evolve over time.
