COMPOSE_FILE := infra/docker/docker-compose.yml
COMPOSE := docker compose --env-file infra/docker/.env -p forecasting -f $(COMPOSE_FILE)

.PHONY: local-deploy
.PHONY: down
.PHONY: feast-up
.PHONY: feast-down
.PHONY: feast-server-up
.PHONY: feast-apply
.PHONY: feast-plan
.PHONY: feast-list

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