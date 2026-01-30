FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from backend for now as they share dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common and jobs
COPY common/ ./common/
COPY jobs/ ./jobs/

# Set Python path to find 'common'
ENV PYTHONPATH=/app

# Entrypoint is the job runner
# Arguments like --task and --id will be passed by Cloud Run Job execution or local trigger
ENTRYPOINT ["python", "jobs/run_job.py"]
