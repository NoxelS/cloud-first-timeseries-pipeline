---
name: make-infra
description: Manage the docker-compose stack and volumes via Makefile
compatibility: opencode
---

## What I do
Provides commands to deploy, restart, stop, and inspect the project's docker-compose infrastructure.

## When to use me
Use this when you need to start the environment, view container logs, or completely reset the local database/state.

## Available Commands
- `make deploy` - Rebuilds the docker stack, pulls images, and recreates containers (`up -d --force-recreate`).
- `make hard-deploy` - Same as deploy, but hard-removes volumes first. **Warning:** Destroys local database/state.
- `make down` - Stops the stack.
- `make hard-down` - Stops the stack and removes volumes.
- `make compose-validate` - Validate docker compose config.
- `make compose-config` - Prints docker compose config.
- `make compose-ps` - Use to view running services.
- `make compose-logs` - Tails the last 200 logs of the containers.
- `make compose-restart` - Restarts the docker-compose stack.
- `make volumes-size` - Prints disk usage of project docker volumes.