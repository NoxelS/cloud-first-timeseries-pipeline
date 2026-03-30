FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/kafka-bootstrap ./services/kafka-bootstrap
COPY scripts ./scripts

RUN uv sync --project services/kafka-bootstrap --no-dev

CMD ["uv", "run", "--project", "services/kafka-bootstrap", "python", "scripts/bootstrap_kafka_topics.py"]
