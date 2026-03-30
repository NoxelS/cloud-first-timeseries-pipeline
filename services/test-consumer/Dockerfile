FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY shared ./shared
COPY services/test-consumer ./services/test-consumer

RUN uv sync --project services/test-consumer --no-dev

CMD ["uv", "run", "--project", "services/test-consumer", "python", "services/test-consumer/src/main.py"]
