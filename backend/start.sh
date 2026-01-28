#!/bin/bash
set -e

echo "Starting deployment startup script..."

# Run migrations
echo "Verifying database connectivity..."
# Simple check if DB is reachable (using the logger in database.py which runs on import)
python -c "from app.db.database import engine; from sqlalchemy import text; with engine.connect() as conn: conn.execute(text('SELECT 1'))"

echo "Running alembic migrations..."
if alembic upgrade head; then
    echo "Migrations completed successfully."
else
    echo "Migrations failed! Check your DATABASE_URL and database connectivity."
    # We exit here because the app likely won't work without migrations, 
    # but the error message will be visible in the logs.
    exit 1
fi

# Start the application
echo "Starting Uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
