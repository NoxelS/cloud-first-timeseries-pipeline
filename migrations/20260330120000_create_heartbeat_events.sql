CREATE TABLE IF NOT EXISTS "raw"."heartbeat_events" (
    "id" uuid PRIMARY KEY,
    "heartbeat_at" timestamptz NOT NULL,
    "kafka_offsets" jsonb NOT NULL,
    "system_checks" jsonb NOT NULL
);

CREATE INDEX IF NOT EXISTS "ix_heartbeat_events_heartbeat_at"
    ON "raw"."heartbeat_events" ("heartbeat_at");
