# Cloud-First Time Series Pipeline

Bootstrap repository for a cloud-first, event-driven data platform focused on time series forecasting.

## Architecture

Data flow:

External APIs -> Collector microservices -> Kafka topics -> Airflow feature pipelines -> Feast feature store -> Future training pipelines

Core principles:

- Event-driven communication through Kafka
- Stateless containers and single-responsibility services
- Thin orchestration layer in Airflow DAGs
- Reusable shared utilities in `shared/`
- Minimal bootstrap placeholders before business logic

## Repository Structure

```text
infra/
	docker/
		docker-compose.yml
		kafka/
		airflow/
		feast/

services/
	eurostat_collector/
		src/
		tests/
		pyproject.toml
		Dockerfile
	example_source_collector/
		src/
		tests/
		pyproject.toml
		Dockerfile

airflow/
	dags/
		feature_pipeline.py
		training_pipeline.py
	plugins/

feast/
	feature_repo/
		feature_store.yaml
		entities.py
		feature_views.py
		data_sources.py

shared/
	kafka/
		producer.py
		consumer.py
		topics.py
	schemas/
	config/

scripts/
	bootstrap_kafka_topics.py
	materialize_features.py

tests/
	integration/
```

## Dependency Management

The repository is configured for `uv` at the root and includes per-service `pyproject.toml` files for service-local dependencies.

Generate lock data with:

```bash
uv lock
```
