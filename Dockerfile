# Use an explicit Debian release variant for better patch cadence and predictability.
ARG PYTHON_BASE_IMAGE=python:3.12-slim-bookworm

# Build stage: resolve dependencies with uv
FROM ${PYTHON_BASE_IMAGE} AS builder

RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/* \
	&& curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /app
COPY requirements.txt .

# Use uv to create a virtual environment and install dependencies
RUN uv pip install --system -r requirements.txt

# Runtime stage: minimal image with only what's needed
FROM ${PYTHON_BASE_IMAGE}

RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder.
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY dags/ ./dags/
COPY dbt/ ./dbt/
COPY docs/ ./docs/
COPY plugins/ ./plugins/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY README.md ./README.md
COPY CONTEXT.md ./CONTEXT.md
COPY .env.example ./.env.example

# Create airflow home and default directories
RUN mkdir -p /app/logs /app/data

# Expose Airflow web UI port
EXPOSE 8080

# Default command: start Airflow API server
CMD ["airflow", "api-server"]
