#!/bin/bash
set -e

echo "=== Pro-NLP Backend Startup ==="
echo "PORT: $PORT"

echo "=== Running Database Migrations ==="
# Migrations are pre-checked in CI/CD, but we keep this for consistency.
# If it hangs, Cloud Run will timeout and we'll see it in logs.
alembic upgrade head

echo "=== Starting Uvicorn Server ==="
# Using 0.0.0.0 is critical for Cloud Run
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}


