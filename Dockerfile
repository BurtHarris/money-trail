# Build stage: resolve dependencies with uv
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY requirements.txt .

# Use uv to create a virtual environment and install dependencies
RUN uv pip install --system -r requirements.txt

# Runtime stage: minimal image with only what's needed
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY dags/ ./dags/
COPY dbt/ ./dbt/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY .env.example ./.env.example

# Create airflow home and default directories
RUN mkdir -p /app/logs /app/data

# Expose Airflow web UI port
EXPOSE 8080

# Default command: start Airflow webserver
CMD ["airflow", "webserver"]
