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
# PORT env var is injected by Cloud Run (default 8080)

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
