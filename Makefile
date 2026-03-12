COMPOSE_FILE := infra/docker/docker-compose.yml
COMPOSE := docker compose --env-file infra/docker/.env -p forecasting -f $(COMPOSE_FILE)
KAFKA_SERVICE := kafka-broker
KAFKA_BOOTSTRAP := localhost:9092
KAFKA_BIN := /opt/kafka/bin
TOPIC ?=
GROUP ?=

.PHONY: help deploy hard-deploy bootstrap down hard-down \
	compose-validate compose-config compose-ps compose-logs compose-restart \
	feast-up feast-server-up feast-down feast-plan feast-apply feast-list \
	sync lint format format-check type-check test test-cov security audit ci validate \
	kafka-topics kafka-topic-describe kafka-topic-create kafka-consumer-groups kafka-consumer-lag kafka-consumer-group-describe kafka-consumer-group-delete

help:
	@echo "Common targets:"
	@echo "  deploy / hard-deploy              - Recreate full docker stack"
	@echo "  down / hard-down                  - Stop stack (hard removes volumes)"
	@echo "  compose-validate                  - Validate docker compose config"
	@echo "  lint / type-check / test          - Local CI checks"
	@echo "  ci                                - sync + format-check + lint + type-check + test + security + compose-validate"
	@echo "  feast-up / feast-apply / feast-list - Feast architecture quickstart"
	@echo "Kafka quick access:"
	@echo "  kafka-topics                      - List Kafka topics"
	@echo "  kafka-consumer-groups             - List consumer groups"
	@echo "  kafka-consumer-lag                - Describe all groups (lag view)"
	@echo "  kafka-topic-describe TOPIC=<name> - Describe one topic"
	@echo "  kafka-topic-create TOPIC=<name>   - Create topic (3 partitions, RF=1)"
	@echo "  kafka-consumer-group-describe GROUP=<name> - Describe one consumer group"
	@echo "  kafka-consumer-group-delete GROUP=<name>   - Delete one consumer group"

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

feast-up:
	$(COMPOSE) up -d postgres-feast-init feast-ui

feast-server-up:
	$(COMPOSE) up -d feast-server

feast-down:
	$(COMPOSE) stop feast-ui feast-server

feast-apply:
	$(COMPOSE) run --rm feast-ui feast apply --skip-source-validation

feast-plan:
	$(COMPOSE) run --rm feast-ui feast plan --skip-source-validation

feast-list:
	$(COMPOSE) run --rm feast-ui feast entities list && $(COMPOSE) run --rm feast-ui feast feature-views list

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

type-check:
	uv run ty check

test:
	uv run pytest tests

test-cov:
	uv run pytest --cov --cov-config=pyproject.toml --cov-report=xml tests

security:
	uv run bandit -r . -c pyproject.toml

audit:
	uv run pip-audit

validate: compose-validate lint type-check test

ci: sync format-check lint type-check test security compose-validate

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