FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ cmake \
    && rm -rf /var/lib/apt/lists/*

RUN uv pip install --system \
    "kafka-python>=2.3.0" \
    "matplotlib>=3.10.0" \
    "pandas>=2.3.0" \
    "psycopg[binary]>=3.3.0" \
    "setuptools<81" \
    "ydata-profiling>=4.16.0"

COPY shared ./shared
RUN uv pip install --system /app/shared

COPY services/feature-view-service/src ./services/feature-view-service/src

CMD ["python", "services/feature-view-service/src/main.py"]
