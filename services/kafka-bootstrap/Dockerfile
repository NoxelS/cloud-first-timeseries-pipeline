FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# Install runtime dependency
RUN uv pip install --system "kafka-python>=2.3.0"

# Copy shared library and bootstrap script
COPY shared ./shared
RUN uv pip install --system /app/shared
COPY scripts/bootstrap_kafka_topics.py ./scripts/bootstrap_kafka_topics.py

CMD ["python", "scripts/bootstrap_kafka_topics.py"]