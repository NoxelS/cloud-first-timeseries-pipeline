FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/energy-charts-backfill-service ./services/energy-charts-backfill-service

RUN uv sync --project services/energy-charts-backfill-service --no-dev

CMD ["uv", "run", "--project", "services/energy-charts-backfill-service", "python", "services/energy-charts-backfill-service/src/main.py"]
