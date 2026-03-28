#!/bin/bash
set -e

echo "Starting app..."

echo "Running database migration"
alembic upgrade head
echo "Migration Completed"

echo "Starting FastAPI with Uvicorn..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}"