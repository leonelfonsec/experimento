#!/bin/sh
set -e

echo "🔎 Creando base 'db' si no existe..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${POSTGRES_DB:-postgres}" \
  -tc "SELECT 1 FROM pg_database WHERE datname = 'db'" | grep -q 1 || \
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${POSTGRES_DB:-postgres}" \
  -c "CREATE DATABASE db;"

echo "🗂️ Creando tabla 'bff_control' si no existe..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "db" <<'EOSQL'
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS bff_control (
  tracking_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       text NOT NULL,
  user_id         text,
  idempotency_key text NOT NULL,
  payload_hash    text NOT NULL,
  status          text NOT NULL CHECK (status IN ('RECEIVED','PROCESSING','DONE','FAILED')),
  source_channel  text,
  sqs_message_id  text,
  attempt_count   int  NOT NULL DEFAULT 0,
  last_error      text,
  order_id        uuid,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_bff_idem ON bff_control (tenant_id, idempotency_key);
CREATE INDEX IF NOT EXISTS ix_bff_status ON bff_control (status);
EOSQL