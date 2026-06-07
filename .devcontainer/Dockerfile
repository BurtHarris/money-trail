# syntax=docker/dockerfile:1.7
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

ARG TARGETARCH

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

RUN set -eux; \
    rm -f /etc/apt/sources.list.d/yarn* || true; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        fd-find \
        git \
        jq \
        libpq-dev \
        postgresql-client \
        procps \
        ripgrep \
        sqlite3 \
        xz-utils; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
RUN set -eux; \
    case "${TARGETARCH}" in \
      "arm64") ARCH="arm64" ;; \
      "amd64") ARCH="x64" ;; \
      *) echo "ERROR: Unsupported architecture: ${TARGETARCH}"; exit 1 ;; \
    esac && \
    curl -fsSL https://nodejs.org/dist/v20.15.0/node-v20.15.0-linux-${ARCH}.tar.xz | \
    tar xJ --strip-components=1 -C /usr/local

RUN npm install -g pnpm

RUN git config --system --add safe.directory /workspaces/money-trail

# Install uv globally for all users
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh

# Install Python deps (cached)
COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r /tmp/requirements.txt

USER vscode
WORKDIR /workspaces/money-trail
