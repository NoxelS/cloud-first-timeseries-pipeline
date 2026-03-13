FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN uv pip install --system "kafka-python>=2.3.0" "psycopg[binary]>=3.3.0"

COPY shared ./shared
RUN uv pip install --system /app/shared

COPY services/energy-charts-backfill-service/src ./services/energy-charts-backfill-service/src

CMD ["python", "services/energy-charts-backfill-service/src/main.py"]
