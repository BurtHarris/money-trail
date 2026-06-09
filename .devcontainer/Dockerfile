FROM mcr.microsoft.com/devcontainers/python:1-3.14-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN set -eux; \
    rm -f /etc/apt/sources.list.d/yarn.list /etc/apt/sources.list.d/yarn*.list || true; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    fd-find \
    git \
    jq \
    libpq-dev \
    procps \
    ripgrep \
    sqlite3; \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh; \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/vscode/.cache/uv && chown -R vscode:vscode /home/vscode/.cache

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --system -r /tmp/requirements.txt

USER vscode
WORKDIR /workspaces/money-trail
