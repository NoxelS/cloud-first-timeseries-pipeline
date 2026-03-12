FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir "feast[postgres,redis]>=0.61.0,<0.62.0"

WORKDIR /app/feast/feature_repo
