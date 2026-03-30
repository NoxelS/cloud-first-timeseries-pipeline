FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/heartbeat-consumer ./services/heartbeat-consumer

RUN uv sync --project services/heartbeat-consumer --no-dev

CMD ["uv", "run", "--project", "services/heartbeat-consumer", "python", "services/heartbeat-consumer/src/main.py"]
