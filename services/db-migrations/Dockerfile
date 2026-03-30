FROM arigaio/atlas:latest AS atlas

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY --from=atlas /atlas /usr/local/bin/atlas

COPY pyproject.toml uv.lock atlas.hcl ./
COPY migrations ./migrations
COPY shared ./shared
COPY services/db-migrations ./services/db-migrations

RUN uv sync --project services/db-migrations --no-dev

CMD ["uv", "run", "--project", "services/db-migrations", "python", "services/db-migrations/src/main.py"]
