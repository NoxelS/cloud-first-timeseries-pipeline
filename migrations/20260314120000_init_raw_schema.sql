CREATE SCHEMA IF NOT EXISTS "raw";

CREATE TABLE IF NOT EXISTS "raw"."energy_charts_frequency" (
  "event_id" text NOT NULL,
  "series_id" text NOT NULL,
  "event_timestamp" timestamptz NOT NULL,
  "frequency_hz" double precision NULL,
  "source_region" text NOT NULL,
  "request_id" text NOT NULL,
  "collected_at" timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT "pk_energy_charts_frequency" PRIMARY KEY ("series_id", "event_timestamp")
);

CREATE INDEX IF NOT EXISTS "idx_energy_charts_frequency_event_timestamp"
  ON "raw"."energy_charts_frequency" ("event_timestamp");

CREATE TABLE IF NOT EXISTS "raw"."energy_charts_ingestion_state" (
  "series_id" varchar NOT NULL,
  "pipeline_name" varchar NOT NULL,
  "last_ingested_ts" timestamptz NULL,
  "backfill_cursor_date" date NULL,
  "updated_at" timestamptz NOT NULL DEFAULT now(),
  "status" varchar NOT NULL DEFAULT 'idle',
  CONSTRAINT "pk_energy_charts_ingestion_state" PRIMARY KEY ("series_id", "pipeline_name")
);
