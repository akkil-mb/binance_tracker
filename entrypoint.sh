#!/bin/bash
set -e

echo "Starting app..."

echo "Running database migration"
alembic upgrade head
echo "Migration Completed"

echo "Starting FastAPI with Uvicorn (reload mode)..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload