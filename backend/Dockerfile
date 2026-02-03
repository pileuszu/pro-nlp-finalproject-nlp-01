FROM python:3.11-slim
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Build from Root Context
COPY backend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy Shared Code
COPY common/ ./common/

# Copy Backend Code
COPY backend/ .

ENV PYTHONPATH=/app
# Cloud Run injects the PORT environment variable (default 8080)
# Use the shell to expand PORT, but keep it efficient.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
