FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

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
    docker.io \
    docker-compose \
    fd-find \
    git \
    jq \
    libpq-dev \
    procps \
    ripgrep \
    sqlite3; \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
    amd64) compose_arch="x86_64" ;; \
    arm64) compose_arch="aarch64" ;; \
    *) echo "Unsupported architecture for Docker Compose plugin: $arch" >&2; exit 1 ;; \
    esac; \
    mkdir -p /usr/local/lib/docker/cli-plugins; \
    curl -fsSL "https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-${compose_arch}" \
    -o /usr/local/lib/docker/cli-plugins/docker-compose; \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose; \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/vscode/.cache/uv && chown -R vscode:vscode /home/vscode/.cache

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --system -r /tmp/requirements.txt

USER vscode
WORKDIR /workspaces/money-trail
