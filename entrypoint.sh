#!/bin/bash
# ── Applivo Backend Entrypoint ─────────────────────────────
# Handles database migrations and startup
# ─────────────────────────────────────────────────────────────

set -e

echo "🚀 Starting Applivo Backend..."

# Wait for database to be ready
# (Note: depends_on with healthcheck in docker-compose is better, 
# but this is a double-check)

echo "🔄 Running database migrations..."
# Run migrations using alembic
alembic upgrade heads

echo "✅ Migrations complete. Starting application..."

# Execute the CMD from Dockerfile
exec "$@"
