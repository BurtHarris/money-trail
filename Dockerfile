# syntax=docker/dockerfile:1.7
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

RUN set -eux; \
    rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn*.list || true; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" > /etc/apt/sources.list.d/nodesource.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    build-essential \
    gh \
    git \
    jq \
    libpq-dev \
    nodejs \
    postgresql-client \
    procps \
    sqlite3; \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY requirements.txt .env.example /tmp/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r /tmp/requirements.txt

USER vscode
WORKDIR /workspaces/money-trail
