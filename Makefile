COMPOSE_FILE := infra/docker/docker-compose.yml
COMPOSE := docker compose --env-file infra/docker/.env -p forecasting -f $(COMPOSE_FILE)
KAFKA_SERVICE := kafka-broker
KAFKA_BOOTSTRAP := localhost:9092
KAFKA_BIN := /opt/kafka/bin
TOPIC ?=
GROUP ?=

.DEFAULT_GOAL := help

.PHONY: help deploy hard-deploy bootstrap down hard-down \
	compose-validate compose-config compose-ps compose-logs compose-restart \
	sync lint lint-fix format format-check type-check test test-unit test-integration test-cov security audit ci validate check \
	heartbeat-trigger kafka-topics kafka-topic-describe kafka-topic-create kafka-consumer-groups kafka-consumer-lag kafka-consumer-group-describe kafka-consumer-group-delete volumes-size

help:
	@echo "Common targets:"
	@echo "  deploy / hard-deploy              - Recreate full docker stack"
	@echo "  down / hard-down                  - Stop stack (hard removes volumes)"
	@echo "  compose-validate                  - Validate docker compose config"
	@echo "  format / lint / type-check        - Source quality checks"
	@echo "  test-unit / test-integration      - Focused test suites"
	@echo "  ci                                - sync + format-check + lint + type-check + test + security + compose-validate"
	@echo "  hard-deploy                       - Rebuild stack and recreate Postgres volumes from Atlas migrations"
	@echo "  heartbeat-trigger                 - Run heartbeat snapshot + plot immediately"
	@echo "Kafka quick access:"
	@echo "  kafka-topics                      - List Kafka topics"
	@echo "  kafka-consumer-groups             - List consumer groups"
	@echo "  kafka-consumer-lag                - Describe all groups (lag view)"
	@echo "  kafka-topic-describe TOPIC=<name> - Describe one topic"
	@echo "  kafka-topic-create TOPIC=<name>   - Create topic (3 partitions, RF=1)"
	@echo "  kafka-consumer-group-describe GROUP=<name> - Describe one consumer group"
	@echo "  kafka-consumer-group-delete GROUP=<name>   - Delete one consumer group"
	@echo "  volumes-size                     - Print disk usage of project docker volumes"

deploy:
	$(COMPOSE) down
	$(COMPOSE) pull --ignore-pull-failures
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d --force-recreate

hard-deploy:
	$(COMPOSE) down -v --remove-orphans
	$(COMPOSE) pull --ignore-pull-failures
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d --force-recreate

bootstrap:
	uv run python scripts/bootstrap_kafka_topics.py

down:
	$(COMPOSE) down

hard-down:
	$(COMPOSE) down -v --remove-orphans

compose-validate:
	$(COMPOSE) config >/dev/null

compose-config:
	$(COMPOSE) config

compose-ps:
	$(COMPOSE) ps

compose-logs:
	$(COMPOSE) logs --tail=200

compose-restart:
	$(COMPOSE) restart

sync:
	uv sync

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

type-check:
	uv run ty check --exclude airflow/

test:
	uv run pytest

test-unit:
	uv run pytest -m "not integration" tests services

test-integration:
	uv run pytest -m integration tests

test-cov:
	uv run pytest --cov --cov-config=pyproject.toml --cov-report=xml

security:
	uv run bandit -r . -c pyproject.toml

audit:
	uv run pip-audit

validate: compose-validate lint type-check test

check: format-check lint type-check test

ci: sync format-check lint type-check test security compose-validate

heartbeat-trigger:
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger
	$(COMPOSE) exec -T airflow-scheduler python -m shared.heartbeat.trigger

kafka-topics:
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-topics.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --list'

kafka-topic-describe:
	@if [ -z "$(TOPIC)" ]; then echo "Usage: make kafka-topic-describe TOPIC=<topic_name>"; exit 1; fi
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-topics.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --describe --topic "$(TOPIC)"'

kafka-topic-create:
	@if [ -z "$(TOPIC)" ]; then echo "Usage: make kafka-topic-create TOPIC=<topic_name>"; exit 1; fi
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-topics.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --create --if-not-exists --topic "$(TOPIC)" --partitions 3 --replication-factor 1'

kafka-consumer-groups:
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-consumer-groups.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --list'

kafka-consumer-lag:
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-consumer-groups.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --describe --all-groups'

kafka-consumer-group-describe:
	@if [ -z "$(GROUP)" ]; then echo "Usage: make kafka-consumer-group-describe GROUP=<group_name>"; exit 1; fi
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-consumer-groups.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --describe --group "$(GROUP)"'

kafka-consumer-group-delete:
	@if [ -z "$(GROUP)" ]; then echo "Usage: make kafka-consumer-group-delete GROUP=<group_name>"; exit 1; fi
	$(COMPOSE) exec -T $(KAFKA_SERVICE) bash -lc '$(KAFKA_BIN)/kafka-consumer-groups.sh --bootstrap-server $(KAFKA_BOOTSTRAP) --delete --group "$(GROUP)"'

volumes-size:
	@vols=$$(docker volume ls -q --filter label=com.docker.compose.project=forecasting); \
	if [ -z "$$vols" ]; then \
		echo "No docker volumes found for project 'forecasting'."; \
		exit 0; \
	fi; \
	vols_csv=$$(printf "%s\n" $$vols | tr "\n" ","); \
	export VOLS_CSV="$$vols_csv"; \
	docker system df -v --format '{{json .}}' | uv run python -c "import json,os,re,sys; wanted={v for v in os.environ.get('VOLS_CSV','').split(',') if v}; data=json.load(sys.stdin); vols=data.get('Volumes',[]); units={'B':1,'kB':1000,'MB':1000**2,'GB':1000**3,'TB':1000**4}; to_bytes=lambda s:(lambda m:int(float(m.group(1))*units.get(m.group(2),1)) if m else 0)(re.match(r'^([0-9]+(?:\\.[0-9]+)?)([A-Za-z]+)$$', str(s))); rows=sorted([v for v in vols if v.get('Name') in wanted], key=lambda x: x.get('Name','')); total=sum(to_bytes(v.get('Size','0B')) for v in rows); print('Volume\\tSize\\tLinks'); [print(f\"{v.get('Name')}\\t{v.get('Size','0B')}\\t{v.get('Links','?')}\") for v in rows]; print(f\"TOTAL_BYTES\\t{total}\\t-\")"
