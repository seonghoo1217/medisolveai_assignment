#!/bin/bash
set -euo pipefail

DB_HOST="${MYSQL_HOST:-db}"
DB_PORT="${MYSQL_PORT:-3306}"

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until nc -z "${DB_HOST}" "${DB_PORT}"; do
  sleep 1
done

echo "Running Alembic migrations..."
cd /app/Assignment1
alembic upgrade head
