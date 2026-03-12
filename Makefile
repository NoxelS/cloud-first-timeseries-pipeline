COMPOSE_FILE := infra/docker/docker-compose.yml
COMPOSE := docker compose --env-file infra/docker/.env -p forecasting -f $(COMPOSE_FILE)

.PHONY: local-deploy
.PHONY: down

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