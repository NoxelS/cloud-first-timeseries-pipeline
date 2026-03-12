FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN uv pip install --system "kafka-python>=2.3.0"

COPY shared ./shared
RUN uv pip install --system /app/shared
COPY services/test-consumer/src ./services/test-consumer/src

CMD ["python", "services/test-consumer/src/main.py"]
