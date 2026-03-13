FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# Copy workspace-level files
COPY services/energy-charts-collector ./services/energy-charts-collector

# COPY shared code
COPY shared ./shared

# Install dependencies
RUN uv pip install --system -r /app/services/energy-charts-collector/pyproject.toml
RUN uv pip install --system /app/shared

CMD ["python", "services/energy-charts-collector/src/main.py"]
